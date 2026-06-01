
print("Nhập thông tin người dùng (Nhập 'done' để kết thúc):")
line =  []
while True:
    user_input = input()
    if user_input.lower() == 'done':
        break
    line.append(user_input)
for i in line:
    print(i.upper())