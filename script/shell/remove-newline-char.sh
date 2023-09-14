find . -type f \( -name '*.pem' ! -path '*awscli*' -o -name '*.conf' -o -name '*.bak' -o -name '*.sh' ! -name 'remove-newline-char.sh' \) -exec sed -i 's///g' {} \;
find . -type f \( -name '*.pem' ! -path '*awscli*' -o -name '*.conf' -o -name '*.bak' -o -name '*.sh' ! -name 'remove-newline-char.sh' \) -exec sed -i 's|\r||' {} \;
