from flaskr.Algorithm import Algorithm

import flaskr.helper as h


class Vad_Alg(Algorithm):
    def filter(self, chunk_filename, word):
        return True

    def find_specific_object(self, upload_dir_path, chunks_dir_path, file_name, param, alg_name):
        print("find_specific_object")
        return self.split_by_silence(upload_dir_path, chunks_dir_path, file_name, param, alg_name)


    def split_by_silence(self, upload_dir_path, chunks_dir_path, file_name, param, alg_name):
        print("split_by_silence")

        file_name_without_format = h.remove_file_format_from_name(file_name)

        audio_chunks_path = h.create_alg_dir(chunks_dir_path, file_name_without_format, "VAD")
        print(f"audio chunk path is: {audio_chunks_path}")

        param_indexes, chunks_num, chunks_at_original_audio = self.get_large_audio_transcription(upload_dir_path,
                                                                                                 chunks_dir_path, param,
                                                                                                 file_name)
        print(f"param indexes {param_indexes}")
        print(f"chunkes num {chunks_num}")
        print(f"chunks_at_original_audio {chunks_at_original_audio}")
        if not param_indexes:
            print(f"audio file doesnt contain silence")
            return []

        audio_chunks = []
        
        for i, segment in enumerate(chunks_at_original_audio):
            start = segment[0]
            end = segment[1]
            interval = (start, end)
            print(f"interval is {interval}")
            new_segment_name = h.create_audio_segment(i, i, chunks_dir_path, "vad",
                                                      i, file_name_without_format, alg_name)
            interval = (h.convert_seconds_to_time(start), h.convert_seconds_to_time(end))
            audio_chunks.append(h.Audio_Chunk(new_segment_name, file_name, interval, alg_name))

        h.delete_chunks(chunks_dir_path, file_name_without_format)
        return audio_chunks