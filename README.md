Receipt Parser allows users to parse their receipt using **AI**

<img src="config/receipt_parser/static/icons/main_icon.png" style="width: 10%"/>

# Navigation
1. <a href="#current-features">Current Features </a>
2. <a href="#set-up-windows">Set up (Windows) </a>
3. <a href="#set-up-linux">Set up (Linux) </a>

# Current Features
<h3 id="current-features">Currently implemented features are:</h3>

* Receipt upload
* Receipt parsing using locally running agent (mostly used gemma4:e2b and gemma4:e4b)
* Form allowing user to view and modify model's inference result

# Set up (Windows)
<h3 id="set-up-windows">Set up on a windows machine consists of following steps:</h3>

  1. Install and correctly set up python 3.11 and pip
  2. Install docker desktop
  3. In project's root run:
     
     * `$ docker compose up`
     * `$ py manage.py migrate`
     * `$ py manage.py runserver`

# Set up (Linux)
<h3 id="set-up-linux">Set up (Linux):</h3>
tbd
