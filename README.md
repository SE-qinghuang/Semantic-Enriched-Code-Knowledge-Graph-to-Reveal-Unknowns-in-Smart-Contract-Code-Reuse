## Links of source code, datas, and virtual machine
Due to GitHub's limited capacity, we have uploaded all our source code and data to Google Cloud Drive. You can access this link to our source code and data: https://drive.google.com/file/d/1x1qx9BlyXJ3ugEcKE8po4elh8MTk6mJN/view?usp=share_link.

In addition, to expedite your verification of our paper, we have created a virtual machine that showcases the KG, code recommendation, and crowd-scale coding practice checking applications we developed. You can access this virtual machine from this link: https://drive.google.com/file/d/12wfj2YsqWIkoeZVfyQ26R8WhMaqLAt8B/view?usp=share_link.

To use the virtual machine, please ensure that you have VMware Station installed. You can download and install this software from the following link: https://drive.google.com/file/d/1QItEgEpoGQCHVAwg1nfzSYJZtIo58hM_/view?usp=share_link.


## Environment configuration
To run this project, you must configure your environment with Python and Neo4j. Specifically, you will need Python version 3.6.9 and Neo4j version Community 3.5.28.

To ensure that you have all the necessary packages installed, please use pip to install the following packages: flask==2.0.2, py2neo==2021.0.1, numpy==1.19.5, slither-analyzer==0.7.1, nltk==3.6.2, gensim==3.8.1, pandas==1.1.5, scikit-learn==0.24.2, transformers==4.18.0, torch==1.10.1, torchvision==0.11.2, solc-select==0.2.0, solidity-parser==0.0.7, and crytic-compile==0.1.13.

Furthermore, it's important to note that you'll need to use solc-select to install solc versions 0.4.10-0.4.25. To do so, please use the following command:

```
solc-select install 0.4.10
solc-select install 0.4.11
...
solc-select install 0.4.25
```

## Code
### KG Build
To build the KG, run `KG_code_datas/make_solidity_kg.py` and save the entities and relationships as .csv files in the `node/` and `relations/` folders.

### Save entities and relations into Neo4j

1. Copy all CSV files into the import folder of Neo4j:
```
sudo cp node/node.csv /usr/local/neo4j/neo4j-community-3.5.28/import/
sudo cp relations/* /usr/local/neo4j/neo4j-community-3.5.28/import/
```

2.Use the `neo4j-admin` import command to store them in the database:
```
sudo . /neo4j-admin import --nodes . /import/node.csv --relationships . /import/has_element.csv --relationships . /import/has_enum.csv --relationships . /import/has_event.csv --relationships . /import/has_function.csv --relationships . /import/has_para.csv --relationships . /import/has_returns.csv --relationships . /import/has_structure.csv --relationships . /import/has_variable.csv --relationships . /import/override.csv --relationships ... /import/function_clone.csv --relationships . /import/calls.csv --relationships . /import/cooccurrence.csv
```

### Run the application
1.Open Neo4j:
```
./neo4j start
```

Go to <u>http://0.0.0.0:7474/</u>.
```
username: neo4j
password: 123456
```

2. Run `KG_code_datas/app.py`. Go to <u>http://127.0.0.1:5000/</u> to view the two application web pages.

### Three code recommendation baselines
1.BM25
`KG_code_datas/tools/code_searching.py` contains all variants of the BM25 algorithm.
Our BM25 is integrated directly into the application and can be used in the front-end pages after running `KG_code_datas/app.py`.

2.CodeBERT
`KG_code_datas/Recommendation_Baseline/CodeBert/demo/Recommendation.py` can run all variants of our CodeBERT.

3.Deep Code Search
`KG_code_datas/Recommendation_Baseline/deep-code-search-master/search.py` can run all variants of our Deep Code Search.

### Evaluation source code (`KG_code_datas/Evaluation/*`)

## Data
### Contract source files
`KG_code_datas/semantic-enriched code kg/graph.db` contains our KG database.

### Entities
`KG_code_datas/node/node.csv` contains all entities and attributes obtained by the KG construction process.

### Relations
`KG_code_datas/relations/*` contains all relations obtained by the KG construction process.

### Models
`KG_code_datas/Model/*` and `KG_code_datas/Recommendation_Baseline/*` contain all models involved in the paper.

### Experimental data
`KG_code_datas/Evaluation/*` contains all experimental data in the paper.


## Quick Start Guide for Virtual Machine
To make it easy for you to try our approach, we have provided a pre-built virtual machine. The environment is already set up in the virtual machine, so you can get started quickly.

### Step 1: Install VMware Workstation
To run our virtual machine, you need to install VMware Workstation 16.1.2. Here are the license keys that you can use:
* ZF3R0-FHED2-M80TY-8QYGC-NPKYF
* YF390-0HF8P-M81RQ-2DXQE-M2UT6
* zf71r-dmx85-08dqy-8ymnc-pphv8

### Step 2: Set Up the Virtual Machine
1.Unzip the file "Smart Contract Code KG.zip" that we have provided.

2.Open the virtual machine with VMware Workstation (`Smart Contract Code KG/Smart Contract Code KG`).

3.Start the virtual machine.

4.After a few minutes of loading, you will be prompted to enter the Ubuntu system.

5.Use the username "sekg" and the password "123456" to log in to the system.

6.Open Neo4j to check our knowledge graph:
```
cd /home/sekg/neo4j-community-3.5.28-unix/neo4j-community-3.5.28/bin
./neo4j start
```
Go to the URL <u>http://0.0.0.0:7474/</u> and log in with the username "neo4j" and the password "123456".

7.Use our two applications:
```
cd /home/sekg/KG
python app.py
```

8.Code Recommendation: Enter a natural language query directly, such as "compare strings". Wait for a while to get the recommendation results. Note that the waiting time can be several minutes because the hardware of the virtual machine may not be sufficient.

9.Code Checking: Directly enter a compilable code file, such as the source code in `/home/sekg/KG/demo/arithmetic.sol`. Wait for a while to get the code checking result. Please note that the waiting time may be several minutes because the hardware of the virtual machine may not be sufficient.






