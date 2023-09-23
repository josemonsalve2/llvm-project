//===------ CGOpenMPRuntimeColossus.h - Interface to OpenMP GPU Runtimes ------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// This provides a generalized class for OpenMP runtime code generation
// specialized by GPU targets NVPTX and AMDGCN.
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_LIB_CODEGEN_CGOPENMPRUNTIMECOLOSSUS_H
#define LLVM_CLANG_LIB_CODEGEN_CGOPENMPRUNTIMECOLOSSUS_H

#include "CGOpenMPRuntime.h"
#include "CodeGenFunction.h"
#include "clang/AST/StmtOpenMP.h"

namespace clang {
namespace CodeGen {

// The Colossus runtime needs to translate simple statements
// like if, for, while, etc. into a sequence of calls to the
// runtime functions in poplar. Therefore, we need to override
// a lot of the CodeGenFunction methods to emit the correct
// runtime calls.

class ColossusCodeGenFunction {
private:
  CodeGenModule &CGM;
  CodeGenFunction &CGF;

  typedef const llvm::function_ref<void(ColossusCodeGenFunction & /*CGF*/,
                                        llvm::Function * /*OutlinedFn*/,
                                        const OMPTaskDataTy & /*Data*/)>
      TaskGenTy;

public:
  ColossusCodeGenFunction(CodeGenModule &CGM, CodeGenFunction &CGF)
      : CGM(CGM), CGF(CGF) {}

  void EmitStmt(const Stmt *S, ArrayRef<const Attr *> Attrs = None);
  void EmitIfStmt(const IfStmt &S);
  void EmitForStmt(const ForStmt &S);
  void EmitWhileStmt(const WhileStmt &S);
  void EmitDoStmt(const DoStmt &S);
  void EmitOMPtaskDirective(const OMPExecutableDirective &S);
  void EmitOMPTaskBasedDirective(const OMPExecutableDirective &S,
                                 const OpenMPDirectiveKind CapturedRegion,
                                 const RegionCodeGenTy &BodyGen,
                                 const TaskGenTy &TaskGen, OMPTaskDataTy &Data);
};

class CGOpenMPRuntimeColossus : public CGOpenMPRuntime {
public:
  explicit CGOpenMPRuntimeColossus(CodeGenModule &CGM);

private:
  struct EntryFunctionState {
    SourceLocation Loc;
  };
  /// Emit outlined function for 'target' directive on the NVPTX
  /// device.
  /// \param D Directive to emit.
  /// \param ParentName Name of the function that encloses the target region.
  /// \param OutlinedFn Outlined function value to be defined by this call.
  /// \param OutlinedFnID Outlined function ID value to be defined by this call.
  /// \param IsOffloadEntry True if the outlined function is an offload entry.
  /// An outlined function may not be an entry if, e.g. the if clause always
  /// evaluates to false.
  void emitTargetOutlinedFunction(const OMPExecutableDirective &D,
                                  StringRef ParentName,
                                  llvm::Function *&OutlinedFn,
                                  llvm::Constant *&OutlinedFnID,
                                  bool IsOffloadEntry,
                                  const RegionCodeGenTy &CodeGen) override;

  /// Emit a collection of outlined functions that contain codelets. Each task
  /// is a codelet.
  ///
  /// \param D Directive to emit.
  /// \param ParentName Name of the function that encloses the target region.
  /// \param OutlinedFn Outlined function value to be defined by this call.
  /// \param OutlinedFnID Outlined function ID value to be defined by this call.
  /// \param IsOffloadEntry True if the outlined function is an offload entry.
  /// \param CodeGen Object containing the target statements.
  /// An outlined function may not be an entry if, e.g. the if clause always
  /// evaluates to false.
  void emitCodelets(const OMPExecutableDirective &D, StringRef ParentName,
                    llvm::Function *&OutlinedFn, llvm::Constant *&OutlinedFnID,
                    bool IsOffloadEntry, const RegionCodeGenTy &CodeGen);

  void emitTaskCall(CodeGenFunction &CGF, SourceLocation Loc,
                    const OMPExecutableDirective &D,
                    llvm::Function *TaskFunction, QualType SharedsTy,
                    Address Shareds, const Expr *IfCond,
                    const OMPTaskDataTy &Data) override;
};

} // CodeGen namespace.
} // clang namespace.

#endif // LLVM_CLANG_LIB_CODEGEN_CGOPENMPRUNTIMECOLOSSUS_H
