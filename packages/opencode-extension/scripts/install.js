#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('📦 HtmlGraph OpenCode Extension Installer');
console.log('==========================================');

const extensionDir = path.dirname(__dirname);
const opencodeConfigDir = path.join(require('os').homedir(), '.opencode', 'extensions', 'htmlgraph');

// Check if this is being run in an OpenCode environment
// OpenCode provides environment variables or other indicators
const isOpenCode = process.env.OPENCODE_VERSION || process.env.OPENCODE_SESSION_ID;

if (!isOpenCode) {
  console.log('⚠️  This extension is designed for OpenCode. Please ensure you\'re running in an OpenCode environment.');
  console.log('   Visit https://opencode.ai for installation instructions.');
  // Don't exit - the extension can still be installed for later use
}

if (isOpenCode) {
  console.log('✅ OpenCode environment detected');
}

// Create extension directory if it doesn't exist
if (!fs.existsSync(opencodeConfigDir)) {
  fs.mkdirSync(opencodeConfigDir, { recursive: true });
  console.log(`📁 Created extension directory: ${opencodeConfigDir}`);
}

// Copy extension files
const filesToCopy = [
  'opencode-extension.json',
  'hooks',
  'command_*.md'
];

filesToCopy.forEach(pattern => {
  if (pattern.includes('*')) {
    // Handle glob patterns
    const glob = require('glob');
    const files = glob.sync(pattern, { cwd: extensionDir });
    files.forEach(file => {
      const src = path.join(extensionDir, file);
      const dest = path.join(opencodeConfigDir, file);
      fs.copyFileSync(src, dest);
      console.log(`📋 Copied: ${file}`);
    });
  } else {
    const src = path.join(extensionDir, pattern);
    const dest = path.join(opencodeConfigDir, pattern);
    if (fs.existsSync(src)) {
      if (fs.statSync(src).isDirectory()) {
        // Copy directory recursively
        require('fs-extra').copySync(src, dest);
      } else {
        fs.copyFileSync(src, dest);
      }
      console.log(`📋 Copied: ${pattern}`);
    }
  }
});

console.log('');
console.log('🎉 HtmlGraph OpenCode Extension installed successfully!');
console.log('');
console.log('Next steps:');
console.log('1. Restart OpenCode');
console.log('2. The extension will automatically activate');
console.log('');
console.log('For updates: npm update @htmlgraph/opencode-extension');