# Translation with Layout Recovery

## About The Project

This is an implementation of Translation with Layout Recovery.

## Main Structure

 * translation_layoutrecovery
   * Frontend/
   * Backend/
   * Model/
   * request.py
   * requirements.txt
   * README.md

## Installation

1. Clone the repo

   ```sh
   git clone https://github.com/phkhanhtrinh23/translation_layoutrecovery.git
   ```

2. Use any code editor to open the folder **translation_layoutrecovery**.

3. Download the [pre-trained model](https://drive.google.com/file/d/1Jx2m_2I1d9PYzFRQ4gl82xQa-G7Vsnsl/view?usp=sharing) of PubLayNet.

4. Create conda virtual environment: `conda create -n translation python=3.9`

5. Install the requirements: `pip install -r requirements.txt`.

6. Run the Back-end API: `python main.py`.

7. Send the request for translation: `python request.py`.

You can send a .pdf file or a directory containing the .pdf files. The translated .pdf files will be saved in the `/outputs` directory.

## Contribution

Contributions are what make GitHub such an amazing place to be learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the project
2. Create your Contribute branch: `git checkout -b contribute/Contribute`
3. Commit your changes: `git commit -m 'add your messages'`
4. Push to the branch: `git push origin contribute/Contribute`
5. Open a pull request

## Contact

Email: phkhanhtrinh23@gmail.com
