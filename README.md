# 5tasy - Translation with Layout Recovery

## 0. Contributors

|            Name               | Profile 
|----------------|-------------------------------
|Nguyễn Bảo Tín | [@nbtin](https://github.com/nbtin)            
|Phạm Khánh Trình | [@phkhanhtrinh23](https://github.com/phkhanhtrinh23)           
|Yang Tuấn Anh | [@YangTuanAnh](https://github.com/YangTuanAnh)
|Nguyễn Hoàng Ngọc Hà | [@ngochafromdn](https://github.com/ngochafromdn)
|Nguyễn Minh Lý | [@lynguyenminh](https://github.com/lynguyenminh)

## 1. Table of Contents
- [1. Table of Contents](#1-table-of-contents)
- [2. About The Project](#2-about-the-project)
- [3. Repo Structure](#3-repo-structure)
- [4. How to Install](#4-how-to-install)
- [5. Usage](#5-usage)
- [6. References](#6-references)

## 2. About The Project

Translation with Layout Recovery is a cutting-edge approach in the field of natural language processing that goes beyond traditional machine translation methods. While conventional translation models focus solely on converting text from one language to another, **5tasy** takes into account the visual layout and formatting of the text. This approach aims to preserve not only the linguistic content but also the spatial arrangement, font styles, and other visual elements present in the source text.

## 3. Repo Structure
```
├── Backend
│   ├── account
│   ├── services
│   └── translation
├── Frontend
│   ├── app
│   │   ├── api
│   │   ├── components
│   │   ├── history
│   │   │   └── api
│   │   ├── login
│   │   │   └── api
│   │   ├── profile
│   │   │   └── api
│   │   └── register
│   │       └── api
│   └── public
└── Model
    └── utils
    └── main.py
```

## 4. How to Install
To install and run the **5tasy** demo web app, please follow the steps below:

1. Ensure that Docker is installed on your system. You can download and install Docker from the official website: [Docker Engine for Ubuntu](https://docs.docker.com/engine/install/ubuntu/) or [Docker Desktop](https://www.docker.com/products/docker-desktop/).

2. Clone this repository to your local machine using the following command:

   ```shell
   git clone https://github.com/phkhanhtrinh23/translation_layoutrecovery.git
   ```

3. Navigate to the project directory:

   ```shell
   cd translation_layoutrecovery
   ```

4. Build the Docker image and run the container using the following command:

   ```shell
   docker compose up --build
   ```

   **Note:** The first time you run the above command, you will need to be patient :smile:. This process may take up to 30 minutes depending on your internet speed. This is because the process involves downloading libraries (also includes some libraries to run on GPU if available).

5. Wait for the installation process to complete. Once the downloading is done, the web app will be ready to use.

## 5. Usage
To use the web app, follow the steps below:

1. Open your web browser and navigate to [http://localhost:3000](http://localhost:3000).

2. In the web app, you can browse and upload an image using the provided interface.
   <img src="images/webUI.png">

3. You first need to register the account and sign in to use the web functions.

4. You can follow the demo web flow.
   <img src="images/webFlow.gif">

5. The model will then process your request and provide answers based on the content of the image. The execution time depends on the number of pages in the original file. The more pages you translate, the more time it takes to execute.
   <img src="imgs/webResult.gif">

## 6. References

- **AutoPrompt** - Taylor Shin, Yasaman Razeghi, Robert L. Logan IV, Eric Wallace, Sameer Singh - [arxiv.org](https://arxiv.org/pdf/2010.15980.pdf)
- **envit5-translation** - Chinh Ngo, Trieu H. Trinh, Long Phan, Hieu Tran, Tai Dang, Hieu Nguyen, Minh Nguyen, Minh-Thang Luong - [huggingface.co](https://huggingface.co/VietAI/envit5-translation).
- **opus-mt-en-jap** - Helsinki-NLP - [huggingface.co](https://huggingface.co/Helsinki-NLP/opus-mt-en-jap).
- **Guides on using Docker for Python application** - [Docker docs](https://docs.docker.com/language/python/).
- **Django REST API UNIT Testing** - Tafadzwa Lameck Nyamukapa - [Video](https://youtu.be/z6_v1UQ9Ht0).
- **Install Docker Engine on Ubuntu** - [Docker docs](https://docs.docker.com/engine/install/ubuntu/).

## Contribution

Contributions are what make GitHub such an amazing place to be learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the project
2. Create your Contribute branch: `git checkout -b contribute/Contribute`
3. Commit your changes: `git commit -m 'add your messages'`
4. Push to the branch: `git push origin contribute/Contribute`
5. Open a pull request
