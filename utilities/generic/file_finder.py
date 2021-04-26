import os
import re

class FileFinder(object):
    def __init__(self, par_id_pattern="EML1_[0-9][0-9][0-9]"):
        self.par_id_pattern = par_id_pattern


    def handle_dictionary_storage(self, _m_dict, _m_key, _m_val, how="append-if-exists"):

        if how == "append-if-exists":
            if _m_key in _m_dict.keys():
                _m_dict[_m_key].append(_m_val)
            else:
                _m_dict[_m_key] = [_m_val]
        elif how == "ignore":
            if _m_key in _m_dict.keys():
                return _m_dict
            else:
                _m_dict[_m_key] = [_m_val]
        else: # overwrite
            _m_dict[_m_key] = [_m_val]

        return _m_dict


    def find_files_of_type(self, dir, suffix, return_parent=False):

        file_dict = {}

        for root, dirs, fnames in os.walk(dir):
            for fname in fnames:
                if fname.endswith(suffix):
                    if return_parent:
                        full_path = root
                    else:
                        full_path = os.path.join(root, fname)
                    participant_id = re.search(self.par_id_pattern, full_path).group()
                    self.handle_dictionary_storage(file_dict, participant_id, full_path, how="append-if-exists")

        return file_dict
