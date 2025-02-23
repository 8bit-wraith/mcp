module.exports = { hooks: { readPackage: (pkg) => { if (pkg.name === 'node-pty') { pkg.scripts = {}; } return pkg; } } };
