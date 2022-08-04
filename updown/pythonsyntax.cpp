//===- PrintTokensSyntax.cpp ----------------------------------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// Replaces syntax outputing the syntax in a python file. 
//
//===----------------------------------------------------------------------===//

#include "clang/Parse/Parser.h"
#include "Jinja2CppLight.h"
#include <fstream>
#include <string>
#include <vector>
#include <utility>
#include "debug.h"
using namespace clang;

#define OUTPUT_PYTHON_FILE "out.py"
namespace {

class PythonHandler : public SyntaxHandler {
private:
  std::vector<std::pair<std::string, std::string>> events;
  std::string originalFileName;

  std::string indentation;
  #ifndef BASE_PATH
  #define BASE_PATH
  #endif

  #define PYTHON_TEMPLATE_FILE BASE_PATH"/templates/python.jinja"
  #define INIT_TEMPLATE_FILE BASE_PATH"/templates/updown_init.jinja"


public:
  PythonHandler() : SyntaxHandler("UpDownPython") { }

  void discoverCheckIndentation(StringRef funcCode) {
    std::string newIndt;
    //Discover Indentation
    for (auto &letter : funcCode.str())
      if (letter == ' ' || letter == '\t')
        newIndt += letter;
      else
        break;

    // First time indentation
    if(this->indentation.size() && newIndt != this->indentation) {
      std::cerr<<"Error with different indentaiton in between multiple python functions"<<std::endl;
      return;
    } else if (!this->indentation.size()) {
      this->indentation = newIndt;
    }
  }

  void generatePythonFile() {
    std::ifstream f(PYTHON_TEMPLATE_FILE);
    std::string TemplateString((std::istreambuf_iterator<char>(f)),
                                  std::istreambuf_iterator<char>());
    Jinja2CppLight::Template PythonTemplate(TemplateString);

    // File to output the python code
    std::ofstream PythonFile(OUTPUT_PYTHON_FILE);
    std::string output;
    llvm::raw_string_ostream OS(output);

    // Create a python function with the same name of the function
    auto find = originalFileName.find(".");
    if (find != std::string::npos)
      originalFileName = originalFileName.substr(0, find);
    OS << "def "<< originalFileName <<"EFA():\n";

    OS << indentation << "efa = EFA([])\n"
       << indentation << "efa.code_level = 'machine'\n"
       << indentation <<"# Adding all the events to the events_map\n"
       << indentation <<"event_map = [{\n";

    int count = 0;
    for (auto &event : events)
      OS << indentation << indentation << "\"" << event.first << "\" : " << count++ << ",\n";
    OS << indentation <<"}]\n\n";
    
    // Dump events
    for (auto &event : events) {
      OS << indentation << "# Adding event " << event.first << "\n";
      // TODO: Check indentation here
      OS << event.second << "\n";
    }

    OS << indentation << "return efa\n";
  
    // Dump the text as-is
    PythonTemplate.setValue("code", OS.str());
    PythonFile << PythonTemplate.render();   
  }

  StringRef getFunctionName(Preprocessor &PP, Declarator &D)
  {
        // Getting the name of the function
    auto FunctionNameRange = Lexer::getAsCharRange(
                D.getName().getSourceRange(), PP.getSourceManager(), PP.getLangOpts());
    return Lexer::getSourceText(FunctionNameRange, PP.getSourceManager(),
                                         PP.getLangOpts());
  }

  StringRef getFunctionText(Preprocessor &PP, CachedTokens &Toks)
  {
    // Get the range in the file that contains the whole text in the function
    // that uses the syntax plugin. The first token may have some indentation.
    // We calculate the beginning of the line. There may be a better way to do this
    // The final location is the end of the final token
    auto beginLoc = Toks.front().getLocation();
    beginLoc = beginLoc.getLocWithOffset(-1*PP.getSourceManager().getSpellingColumnNumber(beginLoc)+1);
    auto endLoc = Toks.back().getEndLoc();
    SourceRange range(beginLoc, endLoc);

    auto FunctionRange = Lexer::getAsCharRange(range, PP.getSourceManager(), PP.getLangOpts());
    return Lexer::getSourceText(FunctionRange, PP.getSourceManager(),
                                      PP.getLangOpts());
  }

  int addEvent(Preprocessor &PP, Declarator &D,
                      CachedTokens &Toks) 
  {
    auto FunctionName = getFunctionName(PP,D);
    auto FunctionText = getFunctionText(PP,Toks);

    events.push_back(std::make_pair(FunctionName.str(), FunctionText.str()));
    return events.size()-1; // Event ID is the position in the vector
  }

  void outputInitFnc(llvm::raw_string_ostream &OS)
  {
    std::ifstream f(INIT_TEMPLATE_FILE);
    std::string TemplateString((std::istreambuf_iterator<char>(f)),
                              std::istreambuf_iterator<char>());
    Jinja2CppLight::Template InitTemplate(TemplateString);
    InitTemplate.setValue("code", "");
    OS << InitTemplate.render();   
  }

  // inline StringRef getParamType(DeclaratorChunk::ParamInfo *Params, uint64_t paramNum) {
  //   if (ParmVarDecl *VarDecl = 
  //         llvm::dyn_cast<ParmVarDecl>(Params[0].Param)) {
  //             auto ParamType =
  //               VarDecl->getOriginalType();
  //             std::string typeName = ParamType.getAsString();
  //         }
  //   return StringRef();
  // }

  inline StringRef getParamName(DeclaratorChunk::ParamInfo *Params, uint64_t paramNum) {
    // if (ParmVarDecl *VarDecl = 
    //     llvm::dyn_cast<ParmVarDecl>(Params[paramNum].Param)) {
    return Params[paramNum].Ident->getName();
    // } else {
    //   llvm_unreachable("This should not have happened. Error getting param Name");
    // }
    return StringRef();
  }

  void GetReplacement(Preprocessor &PP, Declarator &D,
                      CachedTokens &Toks,
                      llvm::raw_string_ostream &OS) override {
    
    // Get name of the first file that gets here
    if (originalFileName.size() == 0) {
      originalFileName = PP.getSourceManager().getFilename(Toks.front().getLocation()).str();
      outputInitFnc(OS);
    }

    discoverCheckIndentation(getFunctionText(PP,Toks));
    auto event_id = addEvent(PP,D,Toks);

    // Rewrite syntax original function and leave it empty for now.
    OS << getDeclText(PP,D) << "{\n";

    unsigned NumParams = D.getFunctionTypeInfo().NumParams;
    DeclaratorChunk::ParamInfo *Params = D.getFunctionTypeInfo().Params;

    if (NumParams > 3) {
      // First three arguments are the lane ID and thread ID
      auto ud_id = getParamName(Params, 0);
      auto lane_id = getParamName(Params, 0);
      auto thread_id = getParamName(Params, 0);
      auto numEventOperands = NumParams - 3; // First 3 operands are UD_ID, LANE_ID and THREAD_ID

      OS << "event_t ev;\n"
         << "ev.setevent_word("<<event_id<<", "<<numEventOperands <<", "<<lane_id<<", " <<thread_id <<");\n";
      
      if (numEventOperands > 0) {
        OS << "operands_t op;\n" 
           << "uint32_t ops_data[" << numEventOperands << "];\n"
           << "uint32_t tmp;\n";
        for (unsigned i = 0; i < numEventOperands; i++) {
          // We need to copy the bits one by one. Let's read it as a pointer
          OS << "tmp = *((uint32_t*)(&"<<getParamName(Params, 3+i)<<"));\n"
             << "ops_data[" << i << "];\n"; // First 3 are decoded above
        }
        OS << "op.setoperands(" << numEventOperands <<", ops_data);\n";
        OS << "send_operands(" << lane_id << ", op);\n";
      }

      OS << "send_event(lane_num, ev);\n";
    }
    
    OS <<"}a\n";
  }

  ~PythonHandler() {
    generatePythonFile();
  }

  void AddToPredefines(llvm::raw_string_ostream &OS) override {
    OS << "#include <stdio.h>\n";
    OS << "#include <updown.h>\n";
  }
};

}

static SyntaxHandlerRegistry::Add<PythonHandler>
X("UpDownPython", "collect all tokens");

