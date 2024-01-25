const fs = require('fs');
const readline = require('readline');
const crypto = require('crypto');

const originalFile = './database.csv';
const fileWithHashedPasswords = './hash_database.csv';
const filteredHashFile = './filtered_database.csv';
const fileStream = fs.createReadStream(originalFile);
const rl = readline.createInterface({ input: fileStream });

const dataArray = [];

rl.on('line', (line) => {
    const values = line.split(',');
    dataArray.push(values);
});

rl.once('close', () => {
    console.log('All data has been read.');

    for (let i = 1; i < dataArray.length; i++) {
        const password = dataArray[i][2].trim(); // Assuming password is in the third column
        dataArray[i][2] = crypto.createHash('sha256').update(password).digest('hex');
    }

    let contentToWrite = dataArray[0].join(',') + '\n';
    for (let i = 1; i < dataArray.length; i++) {
        contentToWrite += dataArray[i].join(', ') + '\n';
    }

    fs.writeFileSync(fileWithHashedPasswords, contentToWrite);

    console.log(`Hashed data has been saved to ${fileWithHashedPasswords}`);
    processHashDatabase();
});

function processHashDatabase() {
    const hashFileStream = fs.createReadStream(fileWithHashedPasswords);
    const hashRl = readline.createInterface({ input: hashFileStream });
    const tempArray = [];
    const filteredHashDataArray = [];

    hashRl.on('line', (line) => {
        const values = line.split(',').map(value => value.trim());
        tempArray.push(values);
    });

    hashRl.once('close', () => {
        const headers = tempArray[0];
        filteredHashDataArray.push(headers);
        let rowIndex = 1;

        for (let i=1; i<tempArray.length; i++) {
            if (!tempArray[i].includes('-')) {
                tempArray[i][0] = rowIndex++;
                // Reorder the row indexes
                filteredHashDataArray.push(tempArray[i]);
            }
        }

        const resultString = filteredHashDataArray.map(row => row.join(', ')).join('\n');
        fs.writeFileSync(filteredHashFile, resultString);
    });
}

