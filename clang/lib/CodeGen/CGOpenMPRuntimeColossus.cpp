//===---- CGOpenMPRuntimeColossus.cpp - Interface to OpenMP GPU Runtimes ----===//
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

#include "CGOpenMPRuntimeColossus.h"
#include "CodeGenFunction.h"
#include "clang/AST/Attr.h"
#include "clang/AST/DeclOpenMP.h"
#include "clang/AST/StmtOpenMP.h"
#include "clang/AST/StmtVisitor.h"
#include "clang/Basic/Cuda.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/Frontend/OpenMP/OMPGridValues.h"
#include "llvm/Support/MathExtras.h"

using namespace clang;
using namespace CodeGen;
using namespace llvm::omp;

///////////////////////////////////////////////////////////////////////////
////////////////////////// HELPER FUNCTIONS ///////////////////////////////
///////////////////////////////////////////////////////////////////////////

static void buildDependences(const OMPExecutableDirective &S,
                             OMPTaskDataTy &Data) {

  printf("Building dependences\n");
  // // First look for 'omp_all_memory' and add this first.
  // bool OmpAllMemory = false;
  // if (llvm::any_of(
  //         S.getClausesOfKind<OMPDependClause>(), [](const OMPDependClause *C)
  //         {
  //           return C->getDependencyKind() == OMPC_DEPEND_outallmemory ||
  //                  C->getDependencyKind() == OMPC_DEPEND_inoutallmemory;
  //         })) {
  //   OmpAllMemory = true;
  //   // Since both OMPC_DEPEND_outallmemory and OMPC_DEPEND_inoutallmemory are
  //   // equivalent to the runtime, always use OMPC_DEPEND_outallmemory to
  //   // simplify.
  //   OMPTaskDataTy::DependData &DD =
  //       Data.Dependences.emplace_back(OMPC_DEPEND_outallmemory,
  //                                     /*IteratorExpr=*/nullptr);
  //   // Add a nullptr Expr to simplify the codegen in emitDependData.
  //   DD.DepExprs.push_back(nullptr);
  // }
  // // Add remaining dependences skipping any 'out' or 'inout' if they are
  // // overridden by 'omp_all_memory'.
  // for (const auto *C : S.getClausesOfKind<OMPDependClause>()) {
  //   OpenMPDependClauseKind Kind = C->getDependencyKind();
  //   if (Kind == OMPC_DEPEND_outallmemory || Kind ==
  //   OMPC_DEPEND_inoutallmemory)
  //     continue;
  //   if (OmpAllMemory && (Kind == OMPC_DEPEND_out || Kind ==
  //   OMPC_DEPEND_inout))
  //     continue;
  //   OMPTaskDataTy::DependData &DD =
  //       Data.Dependences.emplace_back(C->getDependencyKind(),
  //       C->getModifier());
  //   DD.DepExprs.append(C->varlist_begin(), C->varlist_end());
  // }
}

///////////////////////////////////////////////////////////////////////////
////////////////////////// CODEGEN FUNCTIONS //////////////////////////////
///////////////////////////////////////////////////////////////////////////

void ColossusCodeGenFunction::EmitDoStmt(const DoStmt &S) {}

void ColossusCodeGenFunction::EmitWhileStmt(const WhileStmt &S) {}

void ColossusCodeGenFunction::EmitForStmt(const ForStmt &S) {}

void ColossusCodeGenFunction::EmitIfStmt(const IfStmt &S) {}

void ColossusCodeGenFunction::EmitOMPtaskDirective(
    const OMPExecutableDirective &S) {
  printf("Emitting OMP task directive\n");
  // Emit outlined function for task construct.
  const CapturedStmt *CS = S.getCapturedStmt(OMPD_task);

  auto &&BodyGen = [CS](CodeGenFunction &CGF, PrePostActionTy &) {
    CGF.EmitStmt(CS->getCapturedStmt());
  };

  OMPTaskDataTy Data;

  auto &&TaskGen = [&S](ColossusCodeGenFunction &CGF,
                        llvm::Function *OutlinedFn, const OMPTaskDataTy &Data) {

  };

  EmitOMPTaskBasedDirective(S, OMPD_task, BodyGen, TaskGen, Data);
}

void ColossusCodeGenFunction::EmitOMPTaskBasedDirective(
    const OMPExecutableDirective &S, const OpenMPDirectiveKind CapturedRegion,
    const RegionCodeGenTy &BodyGen, const TaskGenTy &TaskGen,
    OMPTaskDataTy &Data) {
  printf("Emitting OMP task based directive\n");
  // Emit outlined function for task construct.
  const CapturedStmt *CS = S.getCapturedStmt(CapturedRegion);
  auto I = CS->getCapturedDecl()->param_begin();
  auto PartId = std::next(I);
  auto TaskT = std::next(I, 4);

  // The first function argument for tasks is a thread id, the second one is a
  // part id (0 for tied tasks, >=0 for untied task).
  llvm::DenseSet<const VarDecl *> EmittedAsPrivate;
  // Get list of private variables.
  for (const auto *C : S.getClausesOfKind<OMPPrivateClause>()) {
    auto IRef = C->varlist_begin();
    for (const Expr *IInit : C->private_copies()) {
      const auto *OrigVD = cast<VarDecl>(cast<DeclRefExpr>(*IRef)->getDecl());
      if (EmittedAsPrivate.insert(OrigVD->getCanonicalDecl()).second) {
        Data.PrivateVars.push_back(*IRef);
        Data.PrivateCopies.push_back(IInit);
      }
      ++IRef;
    }
  }
  EmittedAsPrivate.clear();
  // Get list of firstprivate variables.
  for (const auto *C : S.getClausesOfKind<OMPFirstprivateClause>()) {
    auto IRef = C->varlist_begin();
    auto IElemInitRef = C->inits().begin();
    for (const Expr *IInit : C->private_copies()) {
      const auto *OrigVD = cast<VarDecl>(cast<DeclRefExpr>(*IRef)->getDecl());
      if (EmittedAsPrivate.insert(OrigVD->getCanonicalDecl()).second) {
        Data.FirstprivateVars.push_back(*IRef);
        Data.FirstprivateCopies.push_back(IInit);
        Data.FirstprivateInits.push_back(*IElemInitRef);
      }
      ++IRef;
      ++IElemInitRef;
    }
  }

  // Get list of lastprivate variables (for taskloops).
  llvm::MapVector<const VarDecl *, const DeclRefExpr *> LastprivateDstsOrigs;
  for (const auto *C : S.getClausesOfKind<OMPLastprivateClause>()) {
    auto IRef = C->varlist_begin();
    auto ID = C->destination_exprs().begin();
    for (const Expr *IInit : C->private_copies()) {
      const auto *OrigVD = cast<VarDecl>(cast<DeclRefExpr>(*IRef)->getDecl());
      if (EmittedAsPrivate.insert(OrigVD->getCanonicalDecl()).second) {
        Data.LastprivateVars.push_back(*IRef);
        Data.LastprivateCopies.push_back(IInit);
      }
      LastprivateDstsOrigs.insert(
          std::make_pair(cast<VarDecl>(cast<DeclRefExpr>(*ID)->getDecl()),
                         cast<DeclRefExpr>(*IRef)));
      ++IRef;
      ++ID;
    }
  }
  SmallVector<const Expr *, 4> LHSs;
  SmallVector<const Expr *, 4> RHSs;

  buildDependences(S, Data);

  auto &&CodeGen = [&Data, &S, CS, &BodyGen, &LastprivateDstsOrigs,
                    CapturedRegion](CodeGenFunction &CGF,
                                    PrePostActionTy &Action) { BodyGen(CGF); };

  llvm::Function *OutlinedFn = CGM.getOpenMPRuntime().emitTaskOutlinedFunction(
      S, *I, *PartId, *TaskT, S.getDirectiveKind(), CodeGen, Data.Tied,
      Data.NumberOfParts);

  TaskGen(*this, OutlinedFn, Data);
}

void ColossusCodeGenFunction::EmitStmt(const Stmt *S,
                                       ArrayRef<const Attr *> Attrs) {
  switch (S->getStmtClass()) {
  case Stmt::IfStmtClass:
    EmitIfStmt(cast<IfStmt>(*S));
    break;
  case Stmt::ForStmtClass:
    EmitForStmt(cast<ForStmt>(*S));
    break;
  case Stmt::WhileStmtClass:
    EmitWhileStmt(cast<WhileStmt>(*S));
    break;
  case Stmt::DoStmtClass:
    EmitDoStmt(cast<DoStmt>(*S));
    break;
  case Stmt::OMPTaskDirectiveClass:
    EmitOMPtaskDirective(cast<OMPTaskDirective>(*S));
    break;
  default:
    CGF.EmitStmt(S, Attrs);
    break;
  }
}

CGOpenMPRuntimeColossus::CGOpenMPRuntimeColossus(CodeGenModule &CGM)
    : CGOpenMPRuntime(CGM, "_", "$") {
  if (!CGM.getLangOpts().OpenMPIsDevice)
    llvm_unreachable("OpenMP can only handle device code.");

  llvm::OpenMPIRBuilder &OMPBuilder = getOMPBuilder();
}

void CGOpenMPRuntimeColossus::emitCodelets(const OMPExecutableDirective &D,
                                           StringRef ParentName,
                                           llvm::Function *&OutlinedFn,
                                           llvm::Constant *&OutlinedFnID,
                                           bool IsOffloadEntry,
                                           const RegionCodeGenTy &CodeGen) {

  printf("Calling emitCodelets\n");

  EntryFunctionState EST;

  // Emit target region as a standalone region.
  class ColossusPrePostActionTy : public PrePostActionTy {
    CGOpenMPRuntimeColossus &RT;
    CGOpenMPRuntimeColossus::EntryFunctionState &EST;

  public:
    ColossusPrePostActionTy(CGOpenMPRuntimeColossus &RT,
                            CGOpenMPRuntimeColossus::EntryFunctionState &EST)
        : RT(RT), EST(EST) {}
    void Enter(CodeGenFunction &CGF) override {}
    void Exit(CodeGenFunction &CGF) override {}
  } Action(*this, EST);
  CodeGen.setAction(Action);

  // Emit the body. This should result on eventually emitting tasks. The body
  // should be completely ignored except for the tasks.
  const CapturedStmt &CS = *D.getCapturedStmt(OMPD_target);

  CodeGenFunction CGF(CGM, true);
  ColossusCodeGenFunction CCGF(CGM, CGF);

  // Print source code
  CS.getCapturedDecl()->getBody()->dumpPretty(CGM.getContext());

  auto decl = CS.getCapturedDecl();

  auto body = decl->getBody();
  assert(isa<CompoundStmt>(body) && "Expected a compound statement");

  // change body to compound statement
  CompoundStmt &S = cast<CompoundStmt>(*body);

  // print the stmt class
  const Stmt *ExprResult = S.getStmtExprResult();

  for (auto *CurStmt : S.body()) {
    CCGF.EmitStmt(CurStmt);
  }

  printf("Done emitting target region\n");
}

void CGOpenMPRuntimeColossus::emitTargetOutlinedFunction(
    const OMPExecutableDirective &D, StringRef ParentName,
    llvm::Function *&OutlinedFn, llvm::Constant *&OutlinedFnID,
    bool IsOffloadEntry, const RegionCodeGenTy &CodeGen) {
  if (!IsOffloadEntry) // Nothing to do.
    return;

  assert(!ParentName.empty() && "Invalid target region parent name!");

  // Emit the codelets inside the target region
  emitCodelets(D, ParentName, OutlinedFn, OutlinedFnID, IsOffloadEntry,
               CodeGen);
}

void CGOpenMPRuntimeColossus::emitTaskCall(
    CodeGenFunction &CGF, SourceLocation Loc, const OMPExecutableDirective &D,
    llvm::Function *TaskFunction, QualType SharedsTy, Address Shareds,
    const Expr *IfCond, const OMPTaskDataTy &Data) {

  printf("hereeeee\n");
}
