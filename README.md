<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,30:1a0000,60:660000,100:cc0000&height=220&section=header&text=devilZERO&fontSize=78&fontColor=ffffff&fontAlignY=40&desc=Modular%20DDoS%20Testing%20Toolkit&descSize=20&descAlignY=65&descColor=ff4444&animation=fadeIn&stroke=cc0000&strokeWidth=2" width="100%"/>
</div>

<div align="center">
<img src="https://readme-typing-svg.demolab.com?font=Share+Tech+Mono&size=22&duration=3000&pause=800&color=FF4444&center=true&vCenter=true&width=620&lines=Modular+DDoS+Testing+Toolkit+%F0%9F%92%A5;Layer4+%26+Layer7+Attack+Vectors;Amplification+Attacks+%7C+Proxy+Support;For+Authorized+Security+Assessments+Only;%24+run+devilzero+%E2%80%94+Voktha" alt="Typing SVG"/>
</div>

<br/>

<div align="center">

[![Version](https://img.shields.io/badge/version-2.0.0-06b6d4?style=for-the-badge&labelColor=0d0000)](https://github.com/Vokthos/devilZERO/releases)
&nbsp;
[![Python](https://img.shields.io/badge/Python-3.8+-4ade80?style=for-the-badge&logo=python&logoColor=white&labelColor=0d0000)](https://www.python.org/)
&nbsp;
[![License](https://img.shields.io/badge/License-MIT-8b5cf6?style=for-the-badge&labelColor=0d0000)](LICENSE)
&nbsp;
[![Platform](https://img.shields.io/badge/Kali%20·%20Parrot%20·%20Ubuntu-f97316?style=for-the-badge&logo=linux&logoColor=white&labelColor=0d0000)](https://github.com/Vokthos/devilZERO)

</div>

<br/>

---

## devilZERO — Modular DDoS Testing Toolkit

> Modular DDoS testing toolkit for authorized security assessments and ethical penetration testing.

**Capabilities:**
- **Layer 4:** TCP, UDP, SYN, ICMP floods
- **Layer 7:** HTTP GET/POST floods, Slowloris
- **Amplification:** DNS, NTP, RDP, CLDAP, Memcached, CharGen, ARD
- **Proxy:** Auto-download and rotation from public lists

**⚠️ Ethical Use Only**
For authorized security assessments and educational purposes only.

---

## Installation

### Virtual Environment
```bash
git clone https://github.com/Vokthos/devilZERO.git
cd devilZERO
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
devilzero --help
```

### System-wide (Linux)
```bash
git clone https://github.com/Vokthos/devilZERO.git
cd devilZERO
pip install -r requirements.txt
pip install -e . --break-system-packages
devilzero --help
```

### Docker
```bash
git clone https://github.com/Vokthos/devilZERO.git
cd devilZERO
docker build -t devilzero .
docker run -it devilzero
```

---

## Usage

### Interactive Menu
```bash
┌─[Voktha@redteam]─[~]
└──╼ $ devilzero

  ██████╗ ███████╗██╗   ██╗██╗██╗     ███████╗███████╗██████╗  ██████╗
  ██╔══██╗██╔════╝██║   ██║██║██║     ██╔════╝╚══███╔╝██╔══██╗██╔═══██╗
  ██║  ██║█████╗  ██║   ██║██║██║     █████╗    ███╔╝ ██████╔╝██║   ██║
  ██║  ██║██╔══╝  ╚██╗ ██╔╝██║██║     ██╔══╝   ███╔╝  ██╔══██╗██║   ██║
  ██████╔╝███████╗ ╚████╔╝ ██║███████╗███████╗███████╗██║  ██║╚██████╔╝
  ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝
                         DDoS Testing Toolkit
                     Author: Voktha
                     GitHub: github.com/Vokthos
               Only for authorized security testing!

  1. Layer4 (TCP/UDP/SYN/ICMP)
  2. Layer7 (GET/POST/SLOW)
  3. Amplification (DNS/NTP/RDP/CLDAP/MEM/CHAR/ARD)
  4. Exit
```

### CLI
```bash
# SYN flood (requires root)
sudo devilzero --layer4 [IP] 80 SYN 100 --duration 60

# HTTP flood
devilzero --layer7 http://example.com GET 200 --duration 120

# DNS amplification (requires root)
sudo devilzero --amp [IP] 53 DNS 50 reflectors.txt --duration 60

# Run as Python module
python -m devilzero --help
```

---

## Author

**Voktha** — Red Team Operator

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-Vokthos-ff4444?style=for-the-badge&logo=github&logoColor=white&labelColor=1a0000)](https://github.com/Vokthos)

</div>

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:cc0000,50:660000,100:000000&height=130&section=footer&text=ethical+hacking+only&fontSize=18&fontColor=ff4444&fontAlignY=65&animation=fadeIn" width="100%" alt="Ethical Hacking Only"/>