const XLSX = require('xlsx');
const path = require('path');
const fs = require('fs');

// 读取Excel文件
const excelPath = 'C:/Users/xingh/Desktop/武汉赛维尔生物产品目录20260306.xlsx';
const workbook = XLSX.readFile(excelPath, { type: 'file' });
const worksheet = workbook.Sheets[workbook.SheetNames[0]];

// 转换为JSON
const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });

console.log('Excel列数:', data[0]?.length);
console.log('Excel行数:', data.length);
console.log('表头行:', data[0]);
console.log('数据行示例:', data[2]);

// 输出文件
const outputPath = 'C:/Users/xingh/Desktop/武汉赛维尔生物产品目录_新价格表.xlsx';

// 创建新工作簿
const newWorkbook = XLSX.utils.book_new();

// 表头
const headers = ['中文名称', '英文名称', '销售价', '库存', '分类', '货号', '成本价', '市场价', '图片链接'];
const newData = [headers];

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

// 从第3行开始读取（跳过前两行标题）
let convertedCount = 0;
for (let rowIdx = 2; rowIdx < data.length; rowIdx++) {
    const row = data[rowIdx];
    
    // Excel列对应关系:
    // 0=分类, 1=项目, 2=货号, 3=名称, 4=品牌, 5=规格, 6=价格, 7=备注
    
    const 分类 = cleanText(row[0]);
    const 项目 = cleanText(row[1]);
    const 货号 = cleanText(row[2]);
    const 名称 = cleanText(row[3]);
    const 品牌 = cleanText(row[4]);
    const 规格 = cleanText(row[5]);
    const 价格 = row[6];
    const 备注 = cleanText(row[7]);
    
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
    
    // 英文名称使用"--"
    const 英文名称 = '--';
    
    // 价格计算
    const 销售价 = originalPrice > 0 ? Math.round(originalPrice * 0.9 * 100) / 100 : 0;
    const 成本价 = originalPrice > 0 ? Math.round(originalPrice * 0.7 * 100) / 100 : 0;
    const 市场价 = originalPrice;
    
    // 库存默认1000
    const 库存 = 1000;
    
    // 货号
    const 货号Str = 货号 || '';
    
    // 图片链接为空
    const 图片链接 = '';
    
    // 组合行数据
    const newRow = [
        中文名称,
        英文名称,
        销售价,
        库存,
        分类,
        货号Str,
        成本价,
        市场价,
        图片链接
    ];
    
    newData.push(newRow);
    convertedCount++;
}

// 创建工作表
const newWorksheet = XLSX.utils.aoa_to_sheet(newData);

// 设置列宽
newWorksheet['!cols'] = [
    { wch: 40 },  // 中文名称
    { wch: 15 },  // 英文名称
    { wch: 12 },  // 销售价
    { wch: 10 },  // 库存
    { wch: 15 },  // 分类
    { wch: 15 },  // 货号
    { wch: 12 },  // 成本价
    { wch: 12 },  // 市场价
    { wch: 30 },  // 图片链接
];

// 添加到工作簿
XLSX.utils.book_append_sheet(newWorkbook, newWorksheet, '价格表');

// 保存文件
XLSX.writeFile(newWorkbook, outputPath);

console.log(`\n转换完成！`);
console.log(`共转换 ${convertedCount} 条数据`);
console.log(`输出文件: ${outputPath}`);
