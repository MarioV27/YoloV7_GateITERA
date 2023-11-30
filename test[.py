rows = [[394.0, 216.0, 587.0, 499.0, 0.9577407836914062, 1.0], 0, [908.0, 281.0, 1188.0, 626.0, 0.9084324836730957, 1.0], 1, [436.0, 223.0, 476.0, 272.0, 0.8547171354293823, 0.0], 0, [1022.0, 342.0, 1163.0, 494.0, 0.846112072467804, 4.0], 1, [1049.0, 286.0, 1114.0, 361.0, 0.8311114311218262, 0.0], 1, [1164.0, 374.0, 1175.0, 400.0, 0.7575302720069885, 5.0], 1, [433.0, 263.0, 521.0, 345.0, 0.7556037306785583, 4.0], 0, [1075.0, 560.0, 1119.0, 601.0, 0.7183131575584412, 2.0], 1, [531.0, 279.0, 542.0, 300.0, 0.7010959982872009, 5.0], 0, [456.0, 419.0, 490.0, 449.0, 0.6788949966430664, 2.0], 0] 

names = [
    'Helm',
    'Kendaraan',
    'Pakai Sepatu',
    'Pakaian Terbuka',
    'Pakaian Tertutup',
    'Spion',
    'Tidak Pakai Helm',
    'Tidak Pakai Sepatu'
]

jumlah_motor = 2
motor_indexs = [index for index in range(2)] # [0, 1]
motors = []
label_indexs = []


for motor_index in motor_indexs:
    new_motor = []
    new_label_index = []
    for index, _ in enumerate(rows):
        if index % 2 == 1:
            if motor_index == rows[index]:
                new_motor.append(rows[index-1])
                new_label_index.append(rows[index-1][-1])
    motors.append(new_motor)
    label_indexs.append(new_label_index)


# [[1, 2 , 3, 4, 5, 5], [1, 2 , 3, 4, 5]]
import pdb; pdb.set_trace()
f = open("coba.txt", "w")
row_text = ""
for index in label_indexs:
    row_text += "{}, {}, {}, {}, {}, {}, {}".format(
        index.count(0.0),
        index.count(1.0),
        index.count(2.0),
        index.count(3.0),
        index.count(4.0),
        index.count(5.0),
        index.count(6.0)
    )
    print(index)
    print(row_text)
    print("ganti row")
    # if len(label_indexs)-1 != index:
    #     row_text += "\n"
    
    f.write(row_text)
f.close()

