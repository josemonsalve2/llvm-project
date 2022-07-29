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
using namespace clang;

#define OUTPUT_PYTHON_FILE "out.py"
namespace {

class PythonHandler : public SyntaxHandler {
private:
  std::string TemplateString;
  Jinja2CppLight::Template PythonTemplate;
  std::vector<std::pair<std::string, std::string>> events;
  std::string originalFileName;
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
  }

  void generatePythonFile() {
    
    // File to output the python code
    std::ofstream PythonFile(OUTPUT_PYTHON_FILE);
    std::string output;
    llvm::raw_string_ostream OS(output);

    // Create a pythin function with the same name of the function
    auto find = originalFileName.find(".");
    if (find != std::string::npos)
      originalFileName = originalFileName.substr(0, find);
    OS << "def "<< originalFileName <<"EFA:\n";

    // TODO: Figure out indentation here
    std::string indentation = "    ";

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

  void addEvent(Preprocessor &PP, Declarator &D,
                      CachedTokens &Toks) 
  {
    // Getting the name of the function
    auto FunctionNameRange = Lexer::getAsCharRange(
                D.getName().getSourceRange(), PP.getSourceManager(), PP.getLangOpts());
    auto FunctionName = Lexer::getSourceText(FunctionNameRange, PP.getSourceManager(),
                                         PP.getLangOpts());

    // Get the range in the file that contains the whole text in the function
    // that uses the syntax plugin. The first token may have some indentation.
    // We calculate the beginning of the line. There may be a better way to do this
    // The final location is the end of the final token
    auto beginLoc = Toks.front().getLocation();
    beginLoc = beginLoc.getLocWithOffset(-1*PP.getSourceManager().getSpellingColumnNumber(beginLoc)+1);
    auto endLoc = Toks.back().getEndLoc();
    SourceRange range(beginLoc, endLoc);

    auto FunctionRange = Lexer::getAsCharRange(range, PP.getSourceManager(), PP.getLangOpts());
    auto FunctionText = Lexer::getSourceText(FunctionRange, PP.getSourceManager(),
                                      PP.getLangOpts());

    events.push_back(std::make_pair(FunctionName.str(), FunctionText.str()));
  }

  void GetReplacement(Preprocessor &PP, Declarator &D,
                      CachedTokens &Toks,
                      llvm::raw_string_ostream &OS) override {
    
    // Get name of the first file that gets here
    if (originalFileName.size() == 0) {
      originalFileName = PP.getSourceManager().getFilename(Toks.front().getLocation()).str();
    }
    addEvent(PP,D,Toks);

    // Rewrite syntax original function and leave it empty for now.
    OS << getDeclText(PP,D) << "{\n";
    OS <<"}\n";
  }

  ~PythonHandler() {
    generatePythonFile();
  }

  void AddToPredefines(llvm::raw_string_ostream &OS) override {
    OS << "#include <stdio.h>\n";
  }
};

}

static SyntaxHandlerRegistry::Add<PythonHandler>
X("UpDownPython", "collect all tokens");

