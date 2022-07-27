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
using namespace clang;

namespace {

class PythonHandler : public SyntaxHandler {
private:
  std::string TemplateString;
  Jinja2CppLight::Template PythonTemplate;
  #ifndef BASE_PATH
  #define BASE_PATH
  #endif

  #define TEMPLATE_FILE BASE_PATH"/templates/python.jinja"


public:
  PythonHandler() : SyntaxHandler("UpDownPython"), PythonTemplate("") { 
    std::ifstream f(TEMPLATE_FILE);
    TemplateString = std::string((std::istreambuf_iterator<char>(f)),
                                  std::istreambuf_iterator<char>());
    PythonTemplate = Jinja2CppLight::Template(TemplateString);
    printf("Initializing template "TEMPLATE_FILE"\n");
    printf("TemplateString = %s\n",TemplateString.c_str());

  }

  void GetReplacement(Preprocessor &PP, Declarator &D,
                      CachedTokens &Toks,
                      llvm::raw_string_ostream &OS) override {
    
    std::ofstream PythonFile("out.py");

    OS << "static const char* tokens = \"";
    for (auto &Tok : Toks) {
      OS << " ";
      OS.write_escaped(PP.getSpelling(Tok));
    }
    OS << "\";\n";
    // Rewrite syntax original function.
    OS << getDeclText(PP,D) << "{\n";
    OS << "printf(\"%s\",tokens);\n";
    OS <<"}\n";

    PythonTemplate.setValue("code", OS.str());
    PythonFile << "----\n";
    PythonFile << PythonTemplate.render();
    PythonFile << "----\n";    
    
  }

  void AddToPredefines(llvm::raw_string_ostream &OS) override {
    OS << "#include <stdio.h>\n";
  }
};

}

static SyntaxHandlerRegistry::Add<PythonHandler>
X("UpDownPython", "collect all tokens");

