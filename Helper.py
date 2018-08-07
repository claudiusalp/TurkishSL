import datetime
from Prompt import Prompt
import shutil
import os
import random
import cv2


def sum_time(time_list):
    total = datetime.timedelta()
    for i in time_list:
        total += convert_delta(i)
    return total


def convert_delta(time):
    try:
        (h, m, s) = time.split(':')
    except:
        (m, s) = time.split(':')
        h = 0
    d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(float(s)))
    return d


def sub_time(time1, time2):
    d = convert_delta(time1) - convert_delta(time2)
    print(str(d))


def select_video(start, video_list, video_dif_list_delta):
    video_index = 0
    for i in range(len(video_dif_list_delta)):
        if start > video_dif_list_delta[i]:
            video_index = i
        else:
            break
    return video_list[video_index], start - video_dif_list_delta[video_index]


def word_in(words, sentence):
    if words is None:
        return True
    for word in words:
        if word in sentence:
            return True
    return False


def create_prompts(subs_file):
    prompts = []
    with open(subs_file, 'r', encoding='iso8859_9') as f:
        chunks = f.read().split('\n\n')
        for chunk in chunks:
            if chunk == '':
                continue
            lines = chunk.split('\n')
            prompts.append(Prompt(lines[0], lines[1], lines[2:]))
    return prompts


def safe_create(path):
    try:
        shutil.rmtree(path)
        print(path, 'Deleted')
        os.mkdir(path)
        print(path, 'created.')
    except:
        os.mkdir(path)
        print(path, 'created.')


def find_places(words, video_dif_list_delta, video_list, subs_file):
    prompts = create_prompts(subs_file)
    places = []
    index = 0
    for prompt in prompts:
        if (prompt.content is not None) and len(prompt.sentence) > 2:
            if word_in(words, prompt.sentence):
                start = convert_delta(prompt.interval[0].replace(',', '.'))
                end = convert_delta(prompt.interval[1].replace(',', '.'))
                duration = end - start
                vd, vd_start = select_video(start, video_list, video_dif_list_delta)
                vd_end = vd_start.total_seconds()+duration.total_seconds()
                sb = [vd, index, vd_start.total_seconds(), vd_end, prompt.sentence]
                index += 1
                places.append(sb)
    return places
    ##################

    # random.shuffle(places)
    # size = len(places)
    # train_set = places[:int(size*0.7)]
    # #dev_set = places[int(size*0.7):int(size*0.85)]
    # #test_set = places[int(size*0.85):size]
    # #write_data(train_set,'train.txt')
    # #write_data(test_set,'test.txt')
    # #write_data(dev_set,'dev.txt')
    # return train_set #,dev_set,test_set


def get_frames(video_path, start_time_ms, stop_time_ms, resolution=227, cut_slides=80):
    frames = []
    count = 0
    success = True

    vidcap = cv2.VideoCapture(video_path)

    while success and vidcap.get(cv2.CAP_PROP_POS_MSEC) < start_time_ms:
        success, image = vidcap.read()

    while success and vidcap.get(cv2.CAP_PROP_POS_MSEC) <= stop_time_ms:
        success, image = vidcap.read()
        if cut_slides is not None:
            image = image[:, 80:-80]
        if resolution is not None:
            image = cv2.resize(image, (resolution,resolution))
        frames.append(image)

    return frames


def write_subs(sentence, f):
    for word in sentence:
        f.write(word)
        f.write(" ")
    f.write("\n")


def write_frame(frames, path):
    for i, f in enumerate(frames):
        d = 0.0001 * i
        cv2.imwrite(path + 'frame' + str(d)[2:7] + '.png', f)


def create_dataset(data, type,target_film, new_resolution = 227, cut_sides = 80):
    safe_create('Dataset')
    safe_create('Data')
    dataset_path_tr = 'Dataset/' + type + '.tr'
    dataset_path_sign = 'Dataset/' + type + '.sign'
    file_sign = open(dataset_path_sign, 'w')
    file_tr = open(dataset_path_tr, 'w')
    for i, vd in enumerate(data):
        frames = get_frames(vd[0], vd[2] * 1000, vd[3] * 1000)
        if len(frames) < 1:
            continue
        pwd = os.getcwd()
        frame_path = os.getcwd() + '/Data/' + target_film + '_' + str(vd[1]) + '/'
        sentence = vd[-1]
        ################
        ################
        ################
        safe_create(frame_path)
        write_frame(frames, frame_path)
        file_sign.write(frame_path + "\n")
        write_subs(sentence, file_tr)
        ################
        ################
        ################
    file_tr.close()
    file_sign.close()


