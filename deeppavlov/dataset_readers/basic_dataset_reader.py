# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pathlib import Path

import pandas as pd
from overrides import overrides

from deeppavlov.core.common.registry import register
from deeppavlov.core.data.dataset_reader import DatasetReader
from deeppavlov.core.data.utils import download, mark_done
from deeppavlov.core.common.log import get_logger


log = get_logger(__name__)


@register('basic_dataset_reader')
class BasicDatasetReader(DatasetReader):
    """
    Class provides reading dataset in .csv format and \
    assigns columns with given names to `x` and `y` without any changes of data
    """

    @overrides
    def read(self, data_path: str, url: str = None,
             format: str = "csv",
             *args, **kwargs) -> dict:
        """
        Read dataset from data_path directory.
        Reading files are all data_types + extension
        (i.e for data_types=["train", "valid"] files "train.csv" and "valid.csv" form
        data_path will be read)
        Args:
            data_path: directory with files
            url: download data files if data_path not exists or empty
            format: extension of files. Set of Values: ``"csv", "json"``
            sep (str): delimeter for ``"csv"`` files. Default: ``","``
            header (int): row number to use as the column names
            names (array): list of column names to use
            orient (str): indication of expected JSON string format
            lines (boolean): read the file as a json object per line. Default: ``False``
        Returns:
            dictionary with types from data_types.
            Each field of dictionary is a list of tuples (x_i, y_i)
        """
        data_types = ["train", "valid", "test"]

        train_file = kwargs.get('train', 'train.csv')

        if not Path(data_path, train_file).exists():
            if url is None:
                raise Exception("data path {} does not exist or is empty, and download url parameter not specified!".format(data_path))
            log.info("Loading train data from {} to {}".format(url, data_path))
            download(source_url=url, dest_file_path=Path(data_path, train_file))

        data = {"train": [],
                "valid": [],
                "test": []}
        for data_type in data_types:
            file_name = kwargs.get(data_type, '{}.{}'.format(data_type, format))
            file = Path(data_path).joinpath(file_name)
            if file.exists():
                if format == 'csv':
                    keys = ('sep', 'header', 'names')
                    options = {k: kwargs[k] for k in keys if k in kwargs}
                    df = pd.read_csv(file, **options)
                elif format == 'json':
                    keys = ('orient', 'lines')
                    options = {k: kwargs[k] for k in keys if k in kwargs}
                    df = pd.read_json(file, **options)
                else:
                    raise Exception('Unsupported file format: {}'.format(format))

                x = kwargs.get("x", "text")
                y = kwargs.get('y', "text")

                if isinstance(x, list) and isinstance(y, list):
                    data[data_type] = [([row[x_] for x_ in x], [row[y_] for y_ in y]) for _, row in df.iterrows()]
                elif isinstance(x, list) and not(isinstance(x, list)):
                    data[data_type] = [([row[x_] for x_ in x], row[y]) for _, row in df.iterrows()]
                elif not(isinstance(x, list)) and isinstance(x, list):
                    data[data_type] = [(row[x], [row[y_] for y_ in y]) for _, row in df.iterrows()]
                else:
                    data[data_type] = [(row[x], row[y]) for _, row in df.iterrows()]
            else:
                log.warning("Cannot find {} file".format(file))

        return data