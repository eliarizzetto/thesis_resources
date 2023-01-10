#!python
# Copyright 2019, Silvio Peroni <essepuntato@gmail.com>
# Copyright 2022, Giuseppe Grieco <giuseppe.grieco3@unibo.it>, Arianna Moretti <arianna.moretti4@unibo.it>, Elia Rizzetto <elia.rizzetto@studio.unibo.it>, Arcangelo Massari <arcangelo.massari@unibo.it>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.


from json import loads
from re import match, sub
from time import sleep
from urllib.parse import quote, unquote

from requests import ReadTimeout, get
from requests.exceptions import ConnectionError

from CITS.oc_idmanager.base import IdentifierManager


class RORManager(IdentifierManager):
    """This class implements an identifier manager for ROR identifier"""

    def __init__(self, data={}, use_api_service=True):
        """PMCID manager constructor."""
        super(RORManager, self).__init__()
        self._api = "https://api.ror.org/organizations/"
        self._use_api_service = use_api_service
        self._p = "ror:"
        self._data = data

    def is_valid(self, ror_id, get_extra_info=False):
        ror_id = self.normalise(ror_id, include_prefix=True)

        if ror_id is None or not self.syntax_ok(ror_id):
            return False
        else:
            if ror_id not in self._data or self._data[ror_id] is None:
                if get_extra_info:
                    info = self.exists(ror_id, get_extra_info=True)
                    self._data[ror_id] = info[1]
                    return (info[0] and self.syntax_ok(ror_id)), info[1]
                self._data[ror_id] = dict()
                self._data[ror_id]["valid"] = True if self.exists(ror_id) and self.syntax_ok(ror_id) else False
                return self.exists(ror_id) and self.syntax_ok(ror_id)
            if get_extra_info:
                return self._data[ror_id].get("valid"), self._data[ror_id]
            return self._data[ror_id].get("valid")

    def normalise(self, id_string, include_prefix=False):

        id_string = id_string.lower()
        try:
            ror_id_string = sub(
                "\0+", "", sub("\s+", "", unquote(id_string))
            )
            return "%s%s" % (
                self._p if include_prefix else "",
                ror_id_string.strip(),
            )
        except:
            # Any error in processing the ROR ID will return None
            return None

    def syntax_ok(self, id_string):
        if not id_string.startswith("ror:"):
            id_string = self._p + id_string
        return True if match(r"^ror:((https:\/\/)?ror\.org\/)?0[a-hj-km-np-tv-z|0-9]{6}[0-9]{2}$", id_string) else False

    def exists(self, ror_id_full, get_extra_info=False, allow_extra_api=None):
        valid_bool = True
        if self._use_api_service:
            ror_id = self.normalise(ror_id_full)
            if ror_id is not None:
                tentative = 3
                while tentative:
                    tentative -= 1
                    try:
                        r = get(self._api + quote(ror_id), headers=self._headers, timeout=30)
                        if r.status_code == 200:
                            r.encoding = "utf-8"
                            json_res = loads(r.text)
                            if get_extra_info:
                                return True if json_res['id'] else False, self.extra_info(json_res)
                            return True if json_res['id'] else False
                        elif 400 <= r.status_code < 500:
                            if get_extra_info:
                                return False, {"valid": False}
                            return False
                    except ReadTimeout:
                        # Do nothing, just try again
                        pass
                    except ConnectionError:
                        # Sleep 5 seconds, then try again
                        sleep(5)
                valid_bool = False
            else:
                if get_extra_info:
                    return False, {"valid": False}
                return False

        if get_extra_info:
            return valid_bool, {"valid": valid_bool}
        return valid_bool

    def extra_info(self, api_response, choose_api=None, info_dict={}):
        result = {}
        result["valid"] = True
        # to be implemented
        return result