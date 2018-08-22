def write_to_txt(data_list):
    with open('log.txt','a') as f:
        for key,value in data_list[0].items():
            f.write(key + '\t')
        f.write('\n')
        for data in data_list:
            for key, value in data.items():
                f.write(str(value) + '\t')
            f.write('\n')
        f.close()