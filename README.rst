PS Move Restful API
===================

A super simple REST API for interfacing with Playstation Move controllers using the psmoveapi.

Installation
------------

1. Install the psmoveapi and pair your controllers (probably set aside an evening to get this done, it's not particularly straightforward)

2. Add the full path to the psmoveapi build directory to an environment variable named PSMOVEAPI_BUILD_DIR

2. `pip install -r requirements.txt`

Use
---

Run the server using `python server.py`

Controller information will be hosted at localhost:5000/controllers/<controller_id>
