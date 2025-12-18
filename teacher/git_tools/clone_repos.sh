#!/bin/bash
# Script to clone multiple student repositories into separate directories
# Array of repos with their directory names
declare -A repos=(
    ["angel-moline"]="https://github.com/Angelote567/Ing.-Datos.git"
    ["beatriz-albiac"]="https://github.com/beatrizalbiac/Ing-Datos.git"
    ["blanca-faura"]="https://github.com/blancafaura05-beep/01Ejercicios.git"
    ["carla-domenech"]="https://github.com/Carla55555/data-engineering.git"
    ["carlos-vicente"]="https://github.com/carlitosvy12/Data-Engineering.git"
    ["enrique-garcia"]="https://github.com/Enriquegarciayranzo/Data-Engineer.git"
    ["jorge-molia"]="https://github.com/JMM284/alu.161050.git"
    ["javier-gallardo"]="https://github.com/J4VITXU/Data-Engineer.git"
    ["javier-liarte"]="https://github.com/liliarte-1/ingenieria_de_datos/"
    ["javier-revuelta"]="https://github.com/JavierRevueltaFernandez/Data-Engineering.git"
)

# Clone each repo into its own directory
for name in "${!repos[@]}"; do
    echo "Cloning ${name}..."
    git clone "${repos[$name]}" "$name"
    if [ $? -eq 0 ]; then
        echo "✓ ${name} cloned successfully"
    else
        echo "✗ Failed to clone ${name}"
    fi
done

echo "Done! All repositories cloned into separate directories."