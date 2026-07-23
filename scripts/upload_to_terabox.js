const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

class TeraBoxClient {
    constructor(cookie) {
        this.cookie = cookie;
        // Interceptamos los headers para emular un navegador legítimo
        this.client = axios.create({
            baseURL: 'https://www.terabox.com/api/',
            headers: {
                'Cookie': `ndus=${this.cookie};`,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://www.terabox.com',
                'Referer': 'https://www.terabox.com/main',
            }
        });
    }

    async uploadFile(filePath, remotePath) {
        const fileName = path.basename(filePath);
        const fileSize = fs.statSync(filePath).size;

        console.log(`[+] Iniciando subida: ${fileName} (${fileSize} bytes) a ${remotePath}`);

        try {
            // CORRECCIÓN: Se cambió c-core.terabox.com por www.terabox.com para evitar el ENOTFOUND
            const uploadUrl = 'https://www.terabox.com/rest/2.0/pcs/superfile2';
            
            const form = new FormData();
            form.append('file', fs.createReadStream(filePath));

            console.log('    Transmitiendo payload...');
            
            const response = await this.client.post(uploadUrl, form, {
                headers: {
                    ...form.getHeaders(),
                },
                params: {
                    method: 'upload',
                    path: `${remotePath}/${fileName}`,
                    app_id: 250528 // App ID estándar web de TeraBox
                },
                maxContentLength: Infinity,
                maxBodyLength: Infinity
            });

            if (response.data && !response.data.error_code) {
                console.log(`[EXITO] ${fileName} subido correctamente.`);
                return true;
            } else {
                console.error(`[ERROR] La API rechazó el archivo. Detalles:`, response.data);
                return false;
            }

        } catch (error) {
            console.error(`[ERROR FATAL] Fallo al subir ${fileName}:`, error.response ? error.response.data : error.message);
            return false;
        }
    }
}

async function main() {
    const localDir = process.argv[2];
    const remoteFolder = process.argv[3] || '/Archive';
    const cookie = process.env.TERABOX_COOKIE;

    if (!cookie) {
        console.error("Error Crítico: TERABOX_COOKIE no está configurada en las variables de entorno.");
        process.exit(1);
    }

    if (!localDir || !fs.existsSync(localDir)) {
        console.error(`Error: El directorio local '${localDir}' no existe.`);
        process.exit(1);
    }

    const client = new TeraBoxClient(cookie);
    
    // Obtenemos solo los archivos (ignoramos subdirectorios)
    const files = fs.readdirSync(localDir).filter(f => fs.statSync(path.join(localDir, f)).isFile());

    if (files.length === 0) {
        console.log("No se encontraron archivos en el directorio de descarga.");
        process.exit(0);
    }

    let failedCount = 0;
    for (const file of files) {
        const success = await client.uploadFile(path.join(localDir, file), remoteFolder);
        if (!success) {
            failedCount++;
        }
    }

    if (failedCount > 0) {
        console.error(`\nSubida finalizada con errores en ${failedCount} archivo(s).`);
        process.exit(1);
    } else {
        console.log("\nTodos los archivos se subieron correctamente.");
    }
}

main();
