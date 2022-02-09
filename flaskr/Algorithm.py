import flaskr.helper as h

class Algorithm:

    def filter(self, chunk_filename, param):
        print("filter of alg with pass")
        pass

    # a function that splits the audio file into chunks
    # and applies speech recognition
    def get_large_audio_transcription(self, upload_dir_path, chunks_dir_path, param, file_name):
        # C:\Users\Mirit\PycharmProjects\FinalCsProject\uploads\Welcome2.wav
        # Welcome.wav
        chunks = h.split_audio_to_chunks(upload_dir_path, file_name)

        # remove format from file name (.wav, mp3 etc...)
        file_name = h.remove_file_format_from_name(file_name)

        param_indexs = []
        # chunks start and end in the original audio file
        chunks_at_original_audio = []

        chunk_start = 0
        chunk_end = 0

        # process each chunk
        for i, audio_chunk in enumerate(chunks):
            # export audio chunk and save it in the chunk's directory.
            chunk_filename = h.save_audio_chunk(chunks_dir_path, file_name, audio_chunk, i)

            chunk_end = chunk_start
            chunk_start = chunk_end + len(audio_chunk) / 1000
            chunks_at_original_audio.append((chunk_end, chunk_start))
            if self.filter(chunk_filename, param):
                param_indexs.append((i, param))

        return param_indexs, i, chunks_at_original_audio

    def find_specific_object(self, upload_dir_path, chunks_dir_path, file_name, param):
        param_indexes, chunks_num, chunks_at_original_audio = self.get_large_audio_transcription(upload_dir_path, chunks_dir_path, param, file_name)
        if not param_indexes:
            return f"audio file doesnt contain the word {param}"
        new_segments = h.combine_similar_segments(h.get_relevant_chunks(param_indexes, chunks_num),
                                                chunks_at_original_audio)
        file_name_without_format = h.remove_file_format_from_name(file_name)

        audio_chunks = []
        for i, segment in enumerate(new_segments):
            # segment time interval in original video
            segment_original_time_interval = segment[1]

            # segment interval - tuple (x, y)
            # the created file contain all the chunks from X to Y
            # filename_chunkX.wav - filename_chunkY.wav
            segment_interval = segment[0]
            new_segment_name = h.create_audio_segment(segment_interval[0], segment_interval[1], chunks_dir_path, param, i, file_name_without_format)
            audio_chunks.append(h.Audio_Chunk(new_segment_name, file_name, segment_original_time_interval))

        return audio_chunks