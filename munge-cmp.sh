#!/bin/bash

cd _outputs
for item in *.*; do
  [[ "$item" =~ .req$ ]] && continue
  golden=$item
  if [[ ! -f "golden/$item" ]]; then
    upper_item=${item/abc/ABC}
    if [[ ! -f "golden/$upper_item" ]]; then
      echo "golden/$item does not exist, skipping..."
      continue
    else
      golden=$upper_item
    fi
  fi
  python ../munge-cmp.py $item golden/$golden --atol 0.0001 --rtol 0.001
done