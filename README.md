# VRS-454
![Language](https://img.shields.io/badge/language%20-%20Python-3776AB)
![License](https://img.shields.io/github/license/lina-torovoltas/VRS-454)
![GitHub last commit](https://img.shields.io/github/last-commit/lina-torovoltas/VRS-454)</br>

English internet clone of UVB-76 with ternary XOR encryption and one-time pads.


## Usage

### Clone and install
```bash
git clone https://github.com/lina-torovoltas/VRS-454
cd VRS-454
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the station
```bash
python main.py
```

The server listens on `0.0.0.0:5501` with auto-reload enabled.</br>
Open your browser and navigate to:
```
http://localhost:5501
```


## Configuration
On first run, VRS-454 generates its cipher tables, codemap, and a default password hash automatically.</br>
Before going live, you should:

1. Change the default manager password (`change-password!`) via `/change_password`
2. Set the station callsign via `/change_callsign` (defaults to `VRS-454`)
3. Optionally regenerate the cipher tables and codemap via `/regenerate_tables`


## API
Full endpoint documentation, with usage examples, is served live by the station itself:
```bash
curl http://localhost:5501/manager_guide
```

## Contributing
Contributions are welcome!</br>
If you've found a bug or want to propose an improvement,</br>
feel free to open an issue or submit a pull request.

***
Developed by <a href="https://github.com/lina-torovoltas" style="color:#ff4f00">Lina Torovoltas</a> — © 2026 All rights reserved.