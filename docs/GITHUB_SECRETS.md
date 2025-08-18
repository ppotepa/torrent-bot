# GitHub Actions Secrets Configuration

This document explains how to configure your bot using GitHub Actions secrets for secure deployment.

## 🔐 Required Secrets

Add these secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

### Telegram Configuration
- `TELEGRAM_BOT_TOKEN`: `your_bot_token_from_botfather`

### Jackett Configuration  
- `JACKETT_API_KEY`: `your_jackett_api_key`
- `JACKETT_URL`: `http://jackett:9117` (or your actual Jackett URL)

### qBittorrent Configuration
- `QBITTORRENT_HOST`: `http://qbittorrent:8080` (or your actual qBittorrent URL)
- `QBITTORRENT_USERNAME`: `admin`
- `QBITTORRENT_PASSWORD`: `your_secure_password`

## 🚀 How to Add Secrets

1. Go to your GitHub repository
2. Click `Settings` → `Secrets and variables` → `Actions`
3. Click `New repository secret`
4. Add each secret with the name and value from above

## 📋 Secret Names Reference

```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
JACKETT_API_KEY=your_jackett_api_key
JACKETT_URL=http://jackett:9117
QBITTORRENT_HOST=http://qbittorrent:8080
QBITTORRENT_USERNAME=admin
QBITTORRENT_PASSWORD=your_secure_password
```

## 🔄 Deployment Workflow

The GitHub Actions workflow will:
1. ✅ Check out your code
2. ✅ Set up Python environment
3. ✅ Install dependencies
4. ✅ Create `.env` file from secrets
5. ✅ Test configuration
6. ✅ Build Docker image
7. 🚀 Deploy (configure based on your hosting platform)

## 🛡️ Security Benefits

- ✅ **Encrypted Storage**: Secrets are encrypted at rest
- ✅ **Limited Access**: Only accessible during workflow execution
- ✅ **Audit Trail**: All access is logged
- ✅ **No Code Exposure**: Credentials never appear in your source code
- ✅ **Environment Isolation**: Each deployment gets fresh environment

## 🎯 Usage

### Automatic Deployment
- Push to `master` branch triggers automatic deployment

### Manual Deployment  
- Go to `Actions` tab in GitHub
- Select "Deploy Torrent Bot" workflow
- Click "Run workflow"

## 🔧 Customization

Modify `.github/workflows/deploy.yml` to:
- Add your specific hosting platform deployment steps
- Configure different environments (staging/production)
- Add additional testing or validation steps
- Set up notifications on deployment success/failure

## ⚠️ Important Notes

- Never commit actual secret values to your repository
- Use the local `config-personal` branch for development
- Use GitHub secrets for production deployment
- Regularly rotate your credentials for security
