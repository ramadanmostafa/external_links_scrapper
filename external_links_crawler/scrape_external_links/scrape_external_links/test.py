from helpers import *
from database_functions import *

external_links = {0:"mmm", 1:"mmm", 2:"fds", 3:"mmm", 4:"mmm"}
page_id = 55
anchors = {0:"www", 1:"www2", 2:"zzz", 3:"www", 4:"www2"}
link_type = {0:"follow", 1:"follow", 2:"follow", 3:"follow", 4:"follow"}

save_external_links(external_links, page_id, anchors, link_type)
