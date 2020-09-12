/**
 * @class       : zipTool
 * @author      : cromarmot (yexiaorain@gmail.com)
 * @created     : 星期六 9月 12, 2020 20:38:15 CST
 * @description : zip json with zlib to {data:zipped data}
 * @example     : node zipTool.js in.json out.json
 *                ls -1 lessonData_*.json | xargs -t -i node zipTool.js {} zipped/{}
 */

const zlib = { deflateSync, unzipSync } = require('zlib');
const fs = require('fs');

function zipJson(sourcePath,destPath){
  const data = fs.readFileSync(sourcePath, "utf8");
  const buffer = deflateSync(data);
  fs.writeFileSync(destPath,JSON.stringify({data:buffer.toString('base64')}));
};

function unZipJson(sourcePath,destPath){
 const data = fs.readFileSync(sourcePath, "utf8");
 const buffer = Buffer.from(JSON.parse(data).data, 'base64');
 fs.writeFileSync(destPath,unzipSync(buffer).toString());
}

const args = process.argv.slice(2);
if(args.length === 2){
  zipJson(...args);
}
