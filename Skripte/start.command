#!/bin/bash

# Bei muss "$DIR/schreibprojekt.code-workspace" durch den Namen des Textes bei schreibprojekt geändert werden.

DIR="$(cd "$(dirname "$0")" && pwd)"
open -na "Visual Studio Code" --args "$DIR/schreibprojekt.code-workspace"
