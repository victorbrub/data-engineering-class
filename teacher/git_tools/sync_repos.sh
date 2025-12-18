#!/bin/bash

# Array of repos with their directory names and subfolder names
declare -A repos=(
    ["angel-moline"]="https://github.com/Angelote567/Ing.-Datos.git|Ing.-Datos"
    ["beatriz-albiac"]="https://github.com/beatrizalbiac/Ing-Datos.git|Ing-Datos"
    ["blanca-faura"]="https://github.com/blancafaura05-beep/01Ejercicios.git|01Ejercicios"
    ["carla-domenech"]="https://github.com/Carla55555/data-engineering.git|data-engineering"
    ["carlos-vicente"]="https://github.com/carlitosvy12/Data-Engineering.git|Data-Engineering"
    ["enrique-garcia"]="https://github.com/Enriquegarciayranzo/Data-Engineer.git|Data-Engineer"
    ["jorge-molia"]="https://github.com/JMM284/alu.161050.git|alu.161050"
    ["javier-gallardo"]="https://github.com/J4VITXU/Data-Engineer.git|Data-Engineer"
    ["javier-liarte"]="https://github.com/liliarte-1/ingenieria_de_datos/|ingenieria_de_datos"
    ["javier-revuelta"]="https://github.com/JavierRevueltaFernandez/Data-Engineering.git|Data-Engineering"
)


# Clone or pull for each repo
for name in "${!repos[@]}"; do
    IFS='|' read -r url subfolder <<< "${repos[$name]}"
    
    git_path="$name/$subfolder"
    
    if [ -d "$git_path/.git" ]; then
        # It's a git repo, pull it
        echo "Pulling ${name}..."
        cd "$git_path"
        git pull
        if [ $? -eq 0 ]; then
            echo "✓ ${name} pulled successfully"
        else
            echo "✗ Failed to pull ${name}"
        fi
        cd - > /dev/null
    else
        # Not a git repo, clone it (remove old dir first if it exists)
        echo "Cloning ${name}..."
        [ -d "$name" ] && rm -rf "$name"
        git clone "$url" "$name"
        if [ $? -eq 0 ]; then
            echo "✓ ${name} cloned successfully"
        else
            echo "✗ Failed to clone ${name}"
        fi
    fi
done

echo "Done!"