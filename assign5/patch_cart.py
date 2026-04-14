import sys

with open(r'c:\django\assign5\cart-service\cart\views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "cart.items.all().delete()" in line and "cart = Cart.objects.get" in lines[i-1]:
        new_lines.append("            item_ids = request.data.get('item_ids')\n")
        new_lines.append("            if item_ids and isinstance(item_ids, list):\n")
        new_lines.append("                cart.items.filter(id__in=item_ids).delete()\n")
        new_lines.append("            else:\n")
        new_lines.append("                cart.items.all().delete()\n")
    else:
        new_lines.append(line)

with open(r'c:\django\assign5\cart-service\cart\views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
