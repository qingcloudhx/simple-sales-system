const XLSX = require('xlsx');
const fs = require('fs');

// 读取Excel文件
const excelPath = 'C:/Users/xingh/Desktop/武汉赛维尔生物产品目录20260306.xlsx';
const workbook = XLSX.readFile(excelPath, { type: 'file' });
const worksheet = workbook.Sheets[workbook.SheetNames[0]];

// 转换为JSON
const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });

console.log('Excel列数:', data[0]?.length);
console.log('Excel行数:', data.length);

// 输出文件
const outputPath = 'C:/Users/xingh/Desktop/武汉赛维尔生物产品目录_新价格表.csv';

// 表头
const headers = ['中文名称', '英文名称', '销售价', '库存', '分类', '货号', '成本价', '市场价', '图片链接'];

// 辅助函数：提取价格数字
function extractPrice(value) {
    if (!value) return 0;
    if (typeof value === 'number') return value;
    if (typeof value === 'string') {
        const match = value.replace(/,/g, '').match(/[\d.]+/);
        return match ? parseFloat(match[0]) : 0;
    }
    return 0;
}

// 清理文本
function cleanText(value) {
    if (!value) return '';
    return String(value).trim();
}

// 转义CSV特殊字符
function escapeCSV(value) {
    const str = String(value);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return '"' + str.replace(/"/g, '""') + '"';
    }
    return str;
}

// 构建CSV内容
let csvContent = headers.join(',') + '\n';

// 从第3行开始读取（跳过前两行标题）
let convertedCount = 0;
for (let rowIdx = 2; rowIdx < data.length; rowIdx++) {
    const row = data[rowIdx];
    
    const 分类 = cleanText(row[0]);
    const 货号 = cleanText(row[2]);
    const 名称 = cleanText(row[3]);
    const 规格 = cleanText(row[5]);
    const 价格 = row[6];
    
    // 跳过空行
    if (!名称 && !货号) continue;
    
    // 提取价格数字
    const originalPrice = extractPrice(价格);
    
    // 生成中文名称: 名称(规格)
    let 中文名称;
    if (规格) {
        中文名称 = `${名称}(${规格})`;
    } else {
        中文名称 = 名称;
    }
    
    // 价格计算
    const 销售价 = originalPrice > 0 ? Math.round(originalPrice * 0.9 * 100) / 100 : 0;
    const 成本价 = originalPrice > 0 ? Math.round(originalPrice * 0.7 * 100) / 100 : 0;
    const 市场价 = originalPrice;
    
    // 组合行数据
    const newRow = [
        escapeCSV(中文名称),
        '--',
        销售价,
        1000,
        escapeCSV(分类),
        货号,
        成本价,
        市场价,
        ''
    ];
    
    csvContent += newRow.join(',') + '\n';
    convertedCount++;
}

// 写入文件（UTF-8 with BOM for Excel Chinese compatibility）
const BOM = '\uFEFF';
fs.writeFileSync(outputPath, BOM + csvContent, 'utf8');

console.log(`\n转换完成！`);
console.log(`共转换 ${convertedCount} 条数据`);
console.log(`输出文件: ${outputPath}`);
