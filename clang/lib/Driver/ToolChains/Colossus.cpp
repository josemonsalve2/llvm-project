//===--- Colossus.cpp - Colossus Tool and ToolChain Implementations -----*- C++ -*-===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "Colossus.h"
#include "CommonArgs.h"
#include "clang/Config/config.h"
#include "clang/Driver/Compilation.h"
#include "clang/Driver/Distro.h"
#include "clang/Driver/Driver.h"
#include "clang/Driver/DriverDiagnostic.h"
#include "clang/Driver/InputInfo.h"
#include "clang/Driver/Options.h"
#include "llvm/ADT/Optional.h"
#include "llvm/ADT/StringExtras.h"
#include "llvm/Option/ArgList.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/Host.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/Process.h"
#include "llvm/Support/Program.h"
#include "llvm/Support/TargetParser.h"
#include "llvm/Support/VirtualFileSystem.h"
#include <system_error>

using namespace clang::driver;
using namespace clang::driver::toolchains;
using namespace clang::driver::tools;
using namespace clang;
using namespace llvm::opt;

namespace {

} // namespace

void ColossusInstallationDetector::WarnIfUnsupportedVersion() {
}

ColossusInstallationDetector::ColossusInstallationDetector(
    const Driver &D, const llvm::Triple &HostTriple,
    const llvm::opt::ArgList &Args)
    : D(D) {
  struct Candidate {
    std::string Path;
    bool StrictChecking;

    Candidate(std::string Path, bool StrictChecking = false)
        : Path(Path), StrictChecking(StrictChecking) {}
  };
  SmallVector<Candidate, 4> Candidates;

  // In decreasing order so we prefer newer versions to older versions.
  auto &FS = D.getVFS();

  if (Args.hasArg(clang::driver::options::OPT_poplar_path_EQ)) {
    Candidates.emplace_back(
        Args.getLastArgValue(clang::driver::options::OPT_poplar_path_EQ).str());
  } else if (HostTriple.isOSWindows()) {
        D.Diag(diag::err_drv_no_windows_support);
  } else {
    if (!Args.hasArg(clang::driver::options::OPT_poplar_path_ignore_env)) {
      // Try to find colossus binary. If the executable is located in a directory
      // called 'bin/', its parent directory might be a good guess for a valid
      // COLOSSUS installation.
      if (llvm::ErrorOr<std::string> popc =
              llvm::sys::findProgramByName("popc")) {
        SmallString<256> popcAbsolutePath;
        llvm::sys::fs::real_path(*popc, popcAbsolutePath);

        StringRef popcDir = llvm::sys::path::parent_path(popcAbsolutePath);
        if (llvm::sys::path::filename(popcDir) == "bin")
          Candidates.emplace_back(
              std::string(llvm::sys::path::parent_path(popcDir)),
              /*StrictChecking=*/true);
      }
    }

    Candidates.emplace_back(D.SysRoot + "/usr/local/colossus");
  }

  for (const auto &Candidate : Candidates) {
    InstallPath = Candidate.Path;
    if (InstallPath.empty() || !FS.exists(InstallPath))
      continue;

    BinPath = InstallPath + "/bin";
    IncludePath = InstallPath + "/include";

    if (!(FS.exists(IncludePath) && FS.exists(BinPath)))
      continue;

    // On Linux, we have both lib and lib64 directories, and we need to choose
    // based on our triple. 
    //
    // It's sufficient for our purposes to be flexible: If both lib and lib64
    // exist, we choose whichever one matches our triple.  Otherwise, if only
    // lib exists, we use it.
    if (HostTriple.isArch64Bit() && FS.exists(InstallPath + "/lib64"))
      LibPath = InstallPath + "/lib64";
    else if (FS.exists(InstallPath + "/lib"))
      LibPath = InstallPath + "/lib";

    IsValid = true;
    break;
  }
}

// void ColossusInstallationDetector::AddColossusIncludeArgs(
//     const ArgList &DriverArgs, ArgStringList &CC1Args) const {
//   if (!DriverArgs.hasArg(options::OPT_nobuiltininc)) {

//     SmallString<128> P(D.ResourceDir);
//     llvm::sys::path::append(P, "include");
//     CC1Args.push_back(DriverArgs.MakeArgString(P));
//   }

//   if (!isValid()) {
//     D.Diag(diag::err_drv_no_colossus_installation);
//     return;
//   }

//   CC1Args.push_back("-include");
// }

void ColossusInstallationDetector::CheckColossusVersionSupportsArch(
    CudaArch Arch) const {
}

void ColossusInstallationDetector::print(raw_ostream &OS) const {
  if (isValid())
    OS << "Found COLOSSUS installation: " << InstallPath << ", version \n";
}


void COLOSSUS::Backend::ConstructJob(Compilation &C, const JobAction &JA,
                                    const InputInfo &Output,
                                    const InputInfoList &Inputs,
                                    const ArgList &Args,
                                    const char *LinkingOutput) const {
  const auto &TC =
      static_cast<const toolchains::ColossusToolChain &>(getToolChain());
  assert(TC.getTriple().isColossus() && "Wrong platform");

  ArgStringList CmdArgs;

  if (Arg *A = Args.getLastArg(options::OPT_O_Group)) {
    // Map the -O we received to -O{0,1,2,3}.
    //
    // TODO: Perhaps we should map host -O2 to popc -O3. -O3 is popc's
    // default, so it may correspond more closely to the spirit of clang -O2.

    // -O3 seems like the least-bad option when -Osomething is specified to
    // clang but it isn't handled below.
    StringRef OOpt = "3";
    if (A->getOption().matches(options::OPT_O4) ||
        A->getOption().matches(options::OPT_Ofast))
      OOpt = "3";
    else if (A->getOption().matches(options::OPT_O0))
      OOpt = "0";
    else if (A->getOption().matches(options::OPT_O)) {
      // -Os, -Oz, and -O(anything else) map to -O2, for lack of better options.
      OOpt = llvm::StringSwitch<const char *>(A->getValue())
                 .Case("1", "1")
                 .Case("2", "2")
                 .Case("3", "3")
                 .Case("s", "2")
                 .Case("z", "2")
                 .Default("2");
    }
    CmdArgs.push_back(Args.MakeArgString(llvm::Twine("-O") + OOpt));
  } else {
    // If no -O was passed, pass -O0 to popc  
    CmdArgs.push_back("-O0");
  }

  // Pass -v to popc if it was passed to the driver.
  if (Args.hasArg(options::OPT_v))
    CmdArgs.push_back("-v");
  // CmdArgs.push_back("-target=ipu2");
  CmdArgs.push_back("-o");
  const char *OutputFileName = Args.MakeArgString(TC.getInputFilename(Output));
  if (std::string(OutputFileName) != std::string(Output.getFilename()))
    C.addTempFile(OutputFileName);
  CmdArgs.push_back(OutputFileName);
  for (const auto& II : Inputs)
    CmdArgs.push_back(Args.MakeArgString(II.getFilename()));

  // TODO: ADD -Xcolossus 
  // for (const auto& A : Args.getAllArgValues(options::OPT_Xcolossus_popc))
  //   CmdArgs.push_back(Args.MakeArgString(A));
  // TODO: Should this be using bin folder
  const char *Exec;
  Exec = Args.MakeArgString(TC.GetProgramPath("popc"));
  C.addCommand(std::make_unique<Command>(
      JA, *this,
      ResponseFileSupport{ResponseFileSupport::RF_Full, llvm::sys::WEM_UTF8,
                          "--options-file"},
      Exec, CmdArgs, Inputs, Output));
}

void COLOSSUS::Assembler::ConstructJob(Compilation &C, const JobAction &JA,
                                    const InputInfo &Output,
                                    const InputInfoList &Inputs,
                                    const ArgList &Args,
                                    const char *LinkingOutput) const {
  const auto &TC =
      static_cast<const toolchains::ColossusToolChain &>(getToolChain());
  assert(TC.getTriple().isColossus() && "Wrong platform");

  ArgStringList CmdArgs;
  CmdArgs.push_back("-target ipu2");

  if (Arg *A = Args.getLastArg(options::OPT_O_Group)) {
    // Map the -O we received to -O{0,1,2,3}.
    //
    // TODO: Perhaps we should map host -O2 to popc -O3. -O3 is popc's
    // default, so it may correspond more closely to the spirit of clang -O2.

    // -O3 seems like the least-bad option when -Osomething is specified to
    // clang but it isn't handled below.
    StringRef OOpt = "3";
    if (A->getOption().matches(options::OPT_O4) ||
        A->getOption().matches(options::OPT_Ofast))
      OOpt = "3";
    else if (A->getOption().matches(options::OPT_O0))
      OOpt = "0";
    else if (A->getOption().matches(options::OPT_O)) {
      // -Os, -Oz, and -O(anything else) map to -O2, for lack of better options.
      OOpt = llvm::StringSwitch<const char *>(A->getValue())
                 .Case("1", "1")
                 .Case("2", "2")
                 .Case("3", "3")
                 .Case("s", "2")
                 .Case("z", "2")
                 .Default("2");
    }
    CmdArgs.push_back(Args.MakeArgString(llvm::Twine("-O") + OOpt));
  } else {
    // If no -O was passed, pass -O0 to popc
    CmdArgs.push_back("-O0");
  }

  // Pass -v to popc if it was passed to the driver.
  if (Args.hasArg(options::OPT_v))
    CmdArgs.push_back("-v");
  CmdArgs.push_back("--output-file");
  const char *OutputFileName = Args.MakeArgString(TC.getInputFilename(Output));
  if (std::string(OutputFileName) != std::string(Output.getFilename()))
    C.addTempFile(OutputFileName);
  CmdArgs.push_back(OutputFileName);
  for (const auto& II : Inputs)
    CmdArgs.push_back(Args.MakeArgString(II.getFilename()));

  // TODO: ADD -Xcolossus 
  // for (const auto& A : Args.getAllArgValues(options::OPT_Xcolossus_popc))
  //   CmdArgs.push_back(Args.MakeArgString(A));
  // TODO: Should this be using bin folder
  const char *Exec;
  Exec = Args.MakeArgString(TC.GetProgramPath("popc"));
  C.addCommand(std::make_unique<Command>(
      JA, *this,
      ResponseFileSupport{ResponseFileSupport::RF_Full, llvm::sys::WEM_UTF8,
                          "--options-file"},
      Exec, CmdArgs, Inputs, Output));
}


void COLOSSUS::OpenMPLinker::ConstructJob(Compilation &C, const JobAction &JA,
                                       const InputInfo &Output,
                                       const InputInfoList &Inputs,
                                       const ArgList &Args,
                                       const char *LinkingOutput) const {
  const auto &TC =
      static_cast<const toolchains::ColossusToolChain &>(getToolChain());
  assert(TC.getTriple().isColossus() && "Wrong platform");

  ArgStringList CmdArgs;

  // OpenMP uses nvlink to link cubin files. The result will be embedded in the
  // host binary by the host linker.
  assert(!JA.isHostOffloading(Action::OFK_OpenMP) &&
         "CUDA toolchain not expected for an OpenMP host device.");

  if (Output.isFilename()) {
    CmdArgs.push_back("-o");
    CmdArgs.push_back(Output.getFilename());
  } else
    assert(Output.isNothing() && "Invalid output.");

  if (Args.hasArg(options::OPT_v))
    CmdArgs.push_back("-v");

  // Add paths specified in LIBRARY_PATH environment variable as -L options.
  addDirectoryList(Args, CmdArgs, "-L", "LIBRARY_PATH");

  // Add paths for the default clang library path.
  SmallString<256> DefaultLibPath =
      llvm::sys::path::parent_path(TC.getDriver().Dir);
  llvm::sys::path::append(DefaultLibPath, "lib" CLANG_LIBDIR_SUFFIX);
  CmdArgs.push_back(Args.MakeArgString(Twine("-L") + DefaultLibPath));

  for (const auto &II : Inputs) {
    // Currently, we only pass the input files to the linker, we do not pass
    // any libraries that may be valid only for the host.
    if (!II.isFilename())
      continue;

    const char *binF =
        C.getArgs().MakeArgString(getToolChain().getInputFilename(II));

    CmdArgs.push_back(binF);
  }

  const char *Exec =
      Args.MakeArgString(getToolChain().GetProgramPath("echo"));
  C.addCommand(std::make_unique<Command>(
      JA, *this,
      ResponseFileSupport{ResponseFileSupport::RF_Full, llvm::sys::WEM_UTF8,
                          "--options-file"},
      Exec, CmdArgs, Inputs, Output));
}

/// COLOSSUS toolchain.  Our assembler is popc, and our "linker" is fatbinary,
/// which isn't properly a linker but nonetheless performs the step of stitching
/// together object files from the assembler into a single blob.

ColossusToolChain::ColossusToolChain(const Driver &D, const llvm::Triple &Triple,
                             const ToolChain &HostTC, const ArgList &Args,
                             const Action::OffloadKind OK)
    : ToolChain(D, Triple, Args), HostTC(HostTC),
      ColossusInstallation(D, HostTC.getTriple(), Args), OK(OK) {

  if (ColossusInstallation.isValid()) {
    ColossusInstallation.WarnIfUnsupportedVersion();
    getProgramPaths().push_back(std::string(ColossusInstallation.getBinPath()));
  }
  // Lookup binaries into the driver directory, this is used to
  // discover the clang-offload-bundler executable.
  getProgramPaths().push_back(getDriver().Dir);
}

std::string ColossusToolChain::getInputFilename(const InputInfo &Input) const {
  // Only object files are changed, for example assembly files keep their .s
  // extensions.
  if (Input.getType() != types::TY_Object)
    return ToolChain::getInputFilename(Input);

  // Replace extension for object files with cubin because nvlink relies on
  // these particular file names.
  SmallString<256> Filename(ToolChain::getInputFilename(Input));
  llvm::sys::path::replace_extension(Filename, "pg");
  return std::string(Filename.str());
}

void ColossusToolChain::addClangTargetOptions(
    const llvm::opt::ArgList &DriverArgs,
    llvm::opt::ArgStringList &CC1Args,
    Action::OffloadKind DeviceOffloadingKind) const {
  HostTC.addClangTargetOptions(DriverArgs, CC1Args, DeviceOffloadingKind);

  assert((DeviceOffloadingKind == Action::OFK_OpenMP) &&
         "Only OpenMP or CUDA offloading kinds are supported for NVIDIA GPUs.");

  if (DeviceOffloadingKind == Action::OFK_OpenMP &&
      DriverArgs.hasArg(options::OPT_S))
    return;

}

llvm::DenormalMode ColossusToolChain::getDefaultDenormalModeForType(
    const llvm::opt::ArgList &DriverArgs, const JobAction &JA,
    const llvm::fltSemantics *FPType) const {
  assert(JA.getOffloadingDeviceKind() != Action::OFK_Host);
  return llvm::DenormalMode::getIEEE();
}

bool ColossusToolChain::supportsDebugInfoOption(const llvm::opt::Arg *A) const {
  const Option &O = A->getOption();
  return (O.matches(options::OPT_gN_Group) &&
          !O.matches(options::OPT_gmodules)) ||
         O.matches(options::OPT_g_Flag) ||
         O.matches(options::OPT_ggdbN_Group) || O.matches(options::OPT_ggdb) ||
         O.matches(options::OPT_gdwarf) || O.matches(options::OPT_gdwarf_2) ||
         O.matches(options::OPT_gdwarf_3) || O.matches(options::OPT_gdwarf_4) ||
         O.matches(options::OPT_gdwarf_5) ||
         O.matches(options::OPT_gcolumn_info);
}

void ColossusToolChain::adjustDebugInfoKind(
    codegenoptions::DebugInfoKind &DebugInfoKind, const ArgList &Args) const {
    DebugInfoKind = codegenoptions::NoDebugInfo;
}

// void ColossusToolChain::AddColossusIncludeArgs(const ArgList &DriverArgs,
//                                        ArgStringList &CC1Args) const {
//   ColossusInstallation.AddColossusIncludeArgs(DriverArgs, CC1Args);
// }

llvm::opt::DerivedArgList *
ColossusToolChain::TranslateArgs(const llvm::opt::DerivedArgList &Args,
                             StringRef BoundArch,
                             Action::OffloadKind DeviceOffloadKind) const {
  DerivedArgList *DAL =
      HostTC.TranslateArgs(Args, BoundArch, DeviceOffloadKind);
  if (!DAL)
    DAL = new DerivedArgList(Args.getBaseArgs());


  // For OpenMP device offloading, append derived arguments. Make sure
  // flags are not duplicated.
  // Also append the compute capability.
  if (DeviceOffloadKind == Action::OFK_OpenMP) {
    for (Arg *A : Args)
      if (!llvm::is_contained(*DAL, A))
        DAL->append(A);

    return DAL;
  }

  for (Arg *A : Args) {
    DAL->append(A);
  }
  return DAL;
}

Tool *ColossusToolChain::buildAssembler() const {
  return new tools::COLOSSUS::Assembler(*this);
}

Tool *ColossusToolChain::buildLinker() const {
  return new tools::COLOSSUS::OpenMPLinker(*this);
}

void ColossusToolChain::addClangWarningOptions(ArgStringList &CC1Args) const {
  HostTC.addClangWarningOptions(CC1Args);
}

ToolChain::CXXStdlibType
ColossusToolChain::GetCXXStdlibType(const ArgList &Args) const {
  return HostTC.GetCXXStdlibType(Args);
}

void ColossusToolChain::AddClangSystemIncludeArgs(const ArgList &DriverArgs,
                                              ArgStringList &CC1Args) const {
  HostTC.AddClangSystemIncludeArgs(DriverArgs, CC1Args);
}

void ColossusToolChain::AddClangCXXStdlibIncludeArgs(const ArgList &Args,
                                                 ArgStringList &CC1Args) const {
  HostTC.AddClangCXXStdlibIncludeArgs(Args, CC1Args);
}

void ColossusToolChain::AddIAMCUIncludeArgs(const ArgList &Args,
                                        ArgStringList &CC1Args) const {
  HostTC.AddIAMCUIncludeArgs(Args, CC1Args);
}

SanitizerMask ColossusToolChain::getSupportedSanitizers() const {
  // The ColossusToolChain only supports sanitizers in the sense that it allows
  // sanitizer arguments on the command line if they are supported by the host
  // toolchain. The ColossusToolChain will actually ignore any command line
  // arguments for any of these "supported" sanitizers. That means that no
  // sanitization of device code is actually supported at this time.
  //
  // This behavior is necessary because the host and device toolchains
  // invocations often share the command line, so the device toolchain must
  // tolerate flags meant only for the host toolchain.
  return HostTC.getSupportedSanitizers();
}

VersionTuple ColossusToolChain::computeMSVCVersion(const Driver *D,
                                               const ArgList &Args) const {
  return HostTC.computeMSVCVersion(D, Args);
}


clang::driver::Tool *ColossusToolChain::getBackend() const {
  if (!Backend)
    Backend = std::make_unique<COLOSSUS::Backend>(*this);
  return Backend.get();
}

clang::driver::Tool *ColossusToolChain::SelectTool(const JobAction &JA) const {
  Action::ActionClass AC = JA.getKind();
  return ColossusToolChain::getTool(AC);
}

clang::driver::Tool *ColossusToolChain::getTool(Action::ActionClass AC) const {
  switch (AC) {
  default:
    break;
  case Action::ColossusExternalCompilerJobClass:
    return ColossusToolChain::getBackend();
  }
  return ToolChain::getTool(AC);
}