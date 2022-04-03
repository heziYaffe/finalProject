import os

from pydub import AudioSegment
from pydub.silence import split_on_silence


class Audio_Chunk:
    def __init__(self, file_name, original_file_name, original_interval, alg):
        self.file_name = file_name
        self.original_file_name = original_file_name
        self.alg = alg
        self.original_interval = original_interval

    def __str__(self):
        text = "file name: %s\n" \
               "original file name: %s\n"\
               "detect by %s algorithm\n"\
               "audio apper in %s in the original audio" % \
               (self.file_name, self.original_file_name,self.alg, self.original_interval)
        return text

    def serialize(self):
        return {
            'file_name': self.file_name,
            'original_file_name': self.original_file_name,
            'original_interval': self.original_interval,
        }

def create_dir_in_path(parent_directory, dir_name):
    # Directory
    directory = dir_name


    # Parent Directory path
    parent_dir = parent_directory

    # Path
    path = os.path.join(parent_dir, directory)

    # Create the directory if dosent exist
    if not os.path.exists(path):
        os.makedirs(path)
        print("Directory '% s' created" % directory)

def create_alg_dir(chunks_dir_path, file_name, alg):
    file_name = file_name + ".wav"
    create_dir_in_path(chunks_dir_path, file_name)
    path = os.path.join(chunks_dir_path, file_name)
    create_dir_in_path(path, alg)
    return os.path.join(path, alg)

def split_audio_to_chunks(upload_dir_path, file_name):
    path = os.path.join(upload_dir_path, file_name)
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    # split audio sound where silence is 700 milliseconds or more and get chunks
    chunks = split_on_silence(sound,
                              # experiment with this value for your target audio file
                              min_silence_len=500,
                              # adjust this per requirement
                              silence_thresh=sound.dBFS - 14,
                              # keep the silence for 1 second, adjustable as well
                              keep_silence=500,
                              )
    return chunks

# combine segment that contain each other into one segment
def combine_similar_segments(segments, segments_interval):
    new_segments = []
    start = segments[0][0]
    end = segments[0][1]

    for segment in segments:
        segment_start, segment_end = segment[0], segment[1]
        if segment_start <= end:
            end = segment_end
        else:
            new_segments.append(((start, end), (segments_interval[start][0],
                                                segments_interval[end][1])))
            start = segment_start
            end = segment_end

    if (start, end) not in new_segments:
        new_segments.append(((start, end), (int(segments_interval[start][0]),
                                            int(segments_interval[end][1]))))

    return new_segments


# get the 3 chunks before and after the chunk that contain
# the word
def get_relevant_chunks(object_indexs, chunks_num):
    segments = []
    for i in object_indexs:
        if i[0] > 2:
            start = i[0] - 3
        else:
            start = 0
        if i[0] > chunks_num - 2:
            end = chunks_num
        else:
            end = i[0] + 3

        segment = (start, end)
        segments.append(segment)
    return segments


# create new audio named "file_name" that is part of the original
# audio in specific path
def create_audio_segment(start, end, chunks_dir_path, word, segment_num, file_name, alg_name):
    create_alg_dir(chunks_dir_path, file_name, alg_name)
    word_segment = AudioSegment.empty()
    for i in range(end + 1):
        i = start + i
        sound = AudioSegment.from_file(f'{chunks_dir_path}/{file_name}_chunk{i}.wav')
        word_segment += sound
    path = f"{chunks_dir_path}/{file_name}.wav/{alg_name}/{file_name}_{word}_{segment_num}.wav"
    print("path is: " + path)
    word_segment.export(path, format="wav")
    #word_segment.export(f"C:\\Users\\Mirit\\PycharmProjects\\FinalCsProject\\audioChunks\\Welcome2.wav\\VAD/{file_name}_{word}_{segment_num}.wav", format="wav")

    return f"{file_name}_{word}_{segment_num}.wav"

'''
    i = 0
    while True:
        if os.path.exists(f"{chunks_dir_path}/{file_name}_chunk{i}.wav"):
            os.remove(f"{chunks_dir_path}/{file_name}_chunk{i}.wav")
            i += 1
        else:
            break
            '''

def delete_chunks(chunks_dir_path, file_name):
    i = 0
    while True:
        if os.path.exists(f"{chunks_dir_path}/{file_name}_chunk{i}.wav"):
            os.remove(f"{chunks_dir_path}/{file_name}_chunk{i}.wav")
            i += 1
        else:
            break


# remove file format from file name (.mp3, .wav, etc...)
def remove_file_format_from_name(file_name):
    return file_name.split('.')[0]

'''
def find_specific_param(upload_dir_path, chunks_dir_path, file_name, param):
    param_indexes, chunks_num, chunks_at_original_audio = get_large_audio_transcription(upload_dir_path, chunks_dir_path, param, file_name)
    if not param_indexes:
        return f"audio file doesnt contain the word {param}"
    new_segments = combine_similar_segments(get_relevant_chunks(param_indexes, chunks_num),
                                            chunks_at_original_audio)
    file_name_without_format = remove_file_format_from_name(file_name)

    audio_chunks = []
    for i, segment in enumerate(new_segments):
        # segment time interval in original video
        segment_original_time_interval = segment[1]

        # segment interval - tuple (x, y)
        # the created file contain all the chunks from X to Y
        # filename_chunkX.wav - filename_chunkY.wav
        segment_interval = segment[0]
        new_segment_name = create_audio_segment(segment_interval[0], segment_interval[1], chunks_dir_path, param, i, file_name_without_format)
        audio_chunks.append(Audio_Chunk(new_segment_name, file_name, segment_original_time_interval))

    return audio_chunks
'''
'''
# a function that splits the audio file into chunks
# and applies speech recognition
def get_large_audio_transcription(upload_dir_path, chunks_dir_path, param, file_name):
    #Welcome.wav
    chunks = split_audio_to_chunks(upload_dir_path, file_name)

    # remove format from file name (.wav, mp3 etc...)
    file_name = remove_file_format_from_name(file_name)

    param_indexs = []
    # chunks start and end in the original audio file
    chunks_at_original_audio = []

    chunk_start = 0
    chunk_end = 0

    # process each chunk
    for i, audio_chunk in enumerate(chunks):
        # export audio chunk and save it in the chunk's directory.
        chunk_filename = save_audio_chunk(chunks_dir_path, file_name, audio_chunk, i)

        chunk_end = chunk_start
        chunk_start = chunk_end + len(audio_chunk)/1000
        chunks_at_original_audio.append((chunk_end, chunk_start))
        if filter(chunk_filename, param):
            print(i)
            param_indexs.append((i, param))

    return param_indexs, i, chunks_at_original_audio
'''

# export audio chunk and save it in the chunk's directory.
# and return the name of the saved chunk
def save_audio_chunk(chunks_dir_path, file_name, audio_chunk, chunk_num):
    chunk_file_name = os.path.join(chunks_dir_path, f"{file_name}_chunk{chunk_num}.wav")
    audio_chunk.export(chunk_file_name, format="wav")
    return chunk_file_name