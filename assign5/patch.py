import sys

with open(r'c:\django\assign5\order-service\order\views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if "if not cart or not cart.get('items'):" in line and "get_cart_internal" in lines[i-1]:
        # this is the if block. skip the return line
        pass
    if "return Response({'error':" in line and "status=400)" in line and "get('items')" in lines[i-1]:
        # After this line we add our logic
        new_lines.append("\n        # Filter cart items if item_ids is specified\n")
        new_lines.append("        item_ids = request.data.get('item_ids')\n")
        new_lines.append("        if item_ids and isinstance(item_ids, list):\n")
        new_lines.append("            cart['items'] = [item for item in cart['items'] if item.get('id') in item_ids]\n")
        new_lines.append("            if not cart['items']:\n")
        new_lines.append("                return Response({'error': 'Các s?n ph?m dã ch?n không có trong gi? hàng'}, status=400)\n")
        new_lines.append("            subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart['items'])\n")
        new_lines.append("            cart['total'] = float(subtotal)\n\n")

with open(r'c:\django\assign5\order-service\order\views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
