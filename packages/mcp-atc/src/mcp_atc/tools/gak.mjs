#!/usr/bin/env node

import { program } from 'commander';
import chalk from 'chalk';
import { readFileSync, statSync } from 'fs';
import { join, relative } from 'path';
import { fileURLToPath } from 'url';
import { globbySync } from 'globby';
import isTextPath from 'is-text-path';
import prettyBytes from 'pretty-bytes';
import fs from 'fs/promises';
import { parse as parseGitignore } from 'gitignore-parser';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

// ANSI color shortcuts
const dim = chalk.dim;
const blue = chalk.blue;
const yellow = chalk.yellow;
const red = chalk.red;
const green = chalk.green;
const gray = chalk.gray;

// File type to emoji mapping
const FILE_TYPE_EMOJIS = {
	js: '📜', // JavaScript
	mjs: '📜', // JavaScript Module
	py: '🐍', // Python
	rs: '🦀', // Rust
	go: '🐹', // Go
	rb: '💎', // Ruby
	php: '🐘', // PHP
	java: '☕', // Java
	cpp: '⚡', // C++
	c: '⚡', // C
	h: '📋', // Header
	css: '🎨', // CSS
	html: '🌐', // HTML
	md: '📝', // Markdown
	json: '📦', // JSON
	yml: '⚙️', // YAML
	yaml: '⚙️', // YAML
	sh: '🐚', // Shell
	bash: '🐚', // Bash
	txt: '📄', // Text
	default: '📂' // Default
};

// Get emoji for file type
function getFileEmoji(filePath) {
	const ext = filePath.split('.').pop().toLowerCase();
	return FILE_TYPE_EMOJIS[ext] || FILE_TYPE_EMOJIS.default;
}

program
	.name('gak')
	.description('Global Awesome Keywords - Search files for multiple keywords')
	.argument('[keywords...]', 'Keywords to search for')
	.option('-p, --path <path>', 'Search path', '.')
	.option('-b, --binary', 'Include binary files', false)
	.option('-i, --ignore <patterns...>', 'Glob patterns to ignore', ['**/node_modules/**', '**/.git/**'])
	.option('-t, --type <extensions...>', 'File extensions to search (e.g., js,py,txt)', [])
	.option('-c, --context <chars>', 'Number of characters to show around match', 0)
	.option('-cb, --context-before <chars>', 'Number of characters to show before match', 0)
	.option('-ca, --context-after <chars>', 'Number of characters to show after match', 0)
	.option('-l, --lines <count>', 'Number of lines to show around match', 0)
	.option('-lb, --lines-before <count>', 'Number of lines to show before match', 0)
	.option('-la, --lines-after <count>', 'Number of lines to show after match', 0)
	.option('-m, --max-matches <count>', 'Maximum matches per file', Number.MAX_SAFE_INTEGER)
	.option('-C, --case-sensitive', 'Enable case-sensitive search', false)
	.option('-s, --size <limit>', 'Skip files larger than size (e.g., 1mb, 500kb)', '10mb')
	.option('-q, --quiet', 'Only show file names', false)
	.option('--stats', 'Show search statistics', false)
	.option('-ss, --show-skips', 'Show skipped files', false)
	.option('-gi, --git-ignore', 'Use .gitignore patterns', false)
	.version('1.0.0')
	.showHelpAfterError();

program.on('--help', () => {
	console.log('')
	console.log('Imagined by @8bit-wraith(Hue) & @aye.is');
	console.log('');
	console.log('Examples:');
	console.log('  $ gak password                     # Find files containing "password"');
	console.log('  $ gak -p /etc config secure        # Find files with both words in /etc');
	console.log('  $ gak -b api auth                  # Search in all file types');
	console.log('  $ gak -t js,py class method        # Search only in .js and .py files');
	console.log('  $ gak -c 2 TODO                    # Show 2 characters before and after matches');
	console.log('  $ gak -l 2 TODO                    # Show 2 lines before and after matches');
	console.log('  $ gak -s 1mb error                 # Skip files larger than 1MB');
	console.log('  $ gak -q password                  # Only show file names');
});

program.parse();

const options = program.opts();
const keywords = program.args;

if (!keywords.length) {
	program.help();
}

// Convert size limit to bytes
const sizeLimit = options.size.match(/^(\d+)(k|m|g)?b?$/i);
if (!sizeLimit) {
	console.error(red('Invalid size limit format. Use format like: 500kb, 1mb, 2gb'));
	process.exit(1);
}
const multipliers = { k: 1024, m: 1024 * 1024, g: 1024 * 1024 * 1024 };
const bytes = parseInt(sizeLimit[1]) * (sizeLimit[2] ? multipliers[sizeLimit[2].toLowerCase()] : 1);

// Build glob patterns based on file extensions
let patterns = ['**/*'];
if (options.type.length) {
	const extensions = options.type.join(',').split(',').map(ext => ext.startsWith('.') ? ext : `.${ext}`);
	patterns = extensions.map(ext => `**/*${ext}`);
}

// Function to read and parse .gitignore
function getGitignorePatterns() {
	try {
		const gitignorePath = join(options.path, '.gitignore');
		const gitignoreContent = readFileSync(gitignorePath, 'utf-8');
		return parseGitignore(gitignoreContent).patterns;
	} catch (error) {
		console.error(dim(`Could not read .gitignore: ${error.message}`));
		return [];
	}
}

// Main search function
async function search(options) {
	const {
		pattern,
		caseSensitive = false,
		charsBefore = 0,
		charsAfter = 0,
		fileTypes = null,
	} = options;

	try {
		// Convert pattern to RegExp safely, escaping special chars if it's not already a regex
		const isRegex = pattern.startsWith('/') && pattern.endsWith('/');
		const searchPattern = isRegex ?
			pattern.slice(1, -1) : // Remove the slashes for actual regex
			pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escape special chars for literal search

		const keywords = new Set([searchPattern]);

		const stats = {
			filesSearched: 0,
			matchesFound: 0,
			filesSkipped: {
				size: 0,
				binary: 0,
				error: 0
			}
		};

		let foundMatches = false;

		function searchAndDisplayContext(filePath, keywords) {
			const content = readFileSync(filePath, 'utf-8');
			const lines = content.split('\n');
			const matches = new Map();

			// Find matches for all keywords
			keywords.forEach(keyword => {
				const searchRegex = caseSensitive ? new RegExp(keyword, 'g') : new RegExp(keyword, 'gi');
				lines.forEach((line, index) => {
					if (searchRegex.test(line)) {
						if (!matches.has(index)) {
							matches.set(index, { line, keywords: new Set() });
						}
						matches.get(index).keywords.add(keyword);
					}
				});
			});

			if (matches.size > 0) {
				if (!options.quiet) {
					// Show file name with appropriate emoji
					const emoji = getFileEmoji(filePath);
					console.log(`\n${emoji} ${blue(relative(process.cwd(), filePath))}`);
				}

				let matchCount = 0;
				// Sort matches by line number
				const sortedMatches = Array.from(matches.entries()).sort(([a], [b]) => a - b);

				for (const [lineNum, match] of sortedMatches) {
					if (matchCount >= options.maxMatches) break;

					if (options.quiet) {
						console.log(filePath);
						matchCount++;
						continue;
					}

					// Highlight the matching line
					let highlightedLine = match.line;
					match.keywords.forEach(keyword => {
						const regex = caseSensitive ? new RegExp(keyword, 'g') : new RegExp(keyword, 'gi');
						highlightedLine = highlightedLine.replace(regex, yellow('$&'));
					});

					// Get context sizes
					const charsBefore = options.contextBefore || options.context || 0;
					const charsAfter = options.contextAfter || options.context || 0;
					const linesBefore = options.linesBefore || options.lines || 0;
					const linesAfter = options.linesAfter || options.lines || 0;

					if (charsBefore > 0 || charsAfter > 0) {
						// Character-based context
						const matches = [...highlightedLine.matchAll(new RegExp(Array.from(match.keywords).join('|'), caseSensitive ? 'g' : 'gi'))];
						for (const [matchIndex, m] of matches.entries()) {
							// Convert string indices to array indices for proper character handling
							const lineChars = [...highlightedLine];
							const matchStartIdx = [...highlightedLine.slice(0, m.index)].length;
							const matchEndIdx = matchStartIdx + [...m[0]].length;

							// Calculate context boundaries
							const contextStart = Math.max(0, matchStartIdx - charsBefore);
							const contextEnd = Math.min(lineChars.length, matchEndIdx + charsAfter);

							// Extract and join the context parts
							const beforeContext = lineChars.slice(contextStart, matchStartIdx).join('');
							const matchedText = lineChars.slice(matchStartIdx, matchEndIdx).join('');
							const afterContext = lineChars.slice(matchEndIdx, contextEnd).join('');

							// Truncate long lines for better readability
							const maxLineLength = process.stdout.columns || 120;
							const truncateLength = Math.floor((maxLineLength - 30) / 2); // Leave more room for line numbers, match index, and char index

							const truncateLine = (text) => {
								if (text.length <= truncateLength) return text;
								return text.slice(0, truncateLength) + '...';
							};

							const truncatedBefore = truncateLine(beforeContext);
							const truncatedMatch = matchedText.length > truncateLength ?
								matchedText.slice(0, truncateLength) + '...' : matchedText;
							const truncatedAfter = truncateLine(afterContext);

							// Format: [line@char] content
							console.log(
								green(`${lineNum + 1}`) + dim('@') +
								blue(`${m.index}`) + ' ' +
								(contextStart > 0 ? '...' : '') +
								dim(truncatedBefore) +
								yellow(truncatedMatch) +
								dim(truncatedAfter) +
								(contextEnd < lineChars.length ? '...' : '')
							);
						}
					} else if (linesBefore > 0 || linesAfter > 0) {
						// Line-based context
						const contextBefore = Math.max(0, lineNum - linesBefore);
						const contextAfter = Math.min(lines.length, lineNum + linesAfter + 1);

						// Print context lines before
						for (let i = contextBefore; i < lineNum; i++) {
							console.log(dim(`${i + 1}: ${lines[i]}`));
						}

						// Print the matching line
						console.log(green(`${lineNum + 1}`) + dim(':') + ' ' + highlightedLine);

						// Print context lines after
						for (let i = lineNum + 1; i < contextAfter; i++) {
							console.log(dim(`${i + 1}: ${lines[i]}`));
						}
					} else {
						// Just show the matching line
						console.log(green(`${lineNum + 1}`) + dim(':') + ' ' + highlightedLine);
					}

					console.log(''); // Add spacing between matches
					matchCount++;
				}

				stats.matchesFound += matches.size;
				return true;
			}
			return false;
		}

		// Include .gitignore patterns if the option is set
		if (options.gitIgnore) {
			const gitignorePatterns = getGitignorePatterns();
			options.ignore = options.ignore.concat(gitignorePatterns);
		}

		// Search files
		const files = globbySync(patterns, {
			cwd: options.path,
			absolute: true,
			ignore: options.ignore,
			dot: true
		});

		for (const file of files) {
			try {
				// Check if we can access the file first
				try {
					await fs.access(file, fs.constants.R_OK);
				} catch (error) {
					if (error.code === 'EACCES' || error.code === 'EPERM') {
						stats.filesSkipped.error++;
						if (options.showSkips) {
							console.error(dim(`Skipping ${file}: Permission denied`));
						}
						continue;
					}
					throw error; // Re-throw other errors
				}

				const stat = statSync(file);

				// Skip if it's a directory
				if (stat.isDirectory()) {
					stats.filesSkipped.error++;
					if (options.showSkips) {
						console.error(dim(`Skipping directory: ${file}`));
					}
					continue;
				}

				// Skip large files
				if (stat.size > bytes) {
					stats.filesSkipped.size++;
					if (options.showSkips) {
						console.error(dim(`Skipping large file: ${file} (${prettyBytes(stat.size)})`));
					}
					continue;
				}

				// Skip binary files unless explicitly included
				if (!options.binary && !isTextPath(file)) {
					stats.filesSkipped.binary++;
					if (options.showSkips) {
						console.error(dim(`Skipping binary file: ${file}`));
					}
					continue;
				}

				stats.filesSearched++;

				// Search for all keywords in the file
				if (searchAndDisplayContext(file, keywords)) {
					foundMatches = true;
				}
			} catch (error) {
				stats.filesSkipped.error++;
				if (!options.quiet) {
					if (error.code === 'ENOENT') {
						console.error(dim(`File not found: ${file}`));
					} else if (error.code === 'EISDIR') {
						console.error(dim(`Skipping directory: ${file}`));
					} else {
						console.error(dim(`Error processing ${file}: ${error.message}`));
					}
				}
				continue;
			}
		}

		if (!foundMatches) {
			console.log(red('\nNo matches found.'));
		}

		if (options.stats) {
			const duration = ((Date.now() - stats.startTime) / 1000).toFixed(2);
			console.log('\nSearch Statistics:');
			console.log(`  Time: ${duration}s`);
			console.log(`  Files searched: ${stats.filesSearched}`);
			console.log(`  Files with matches: ${stats.matchesFound}`);
			console.log('  Files skipped:');
			console.log(`    Size limit: ${stats.filesSkipped.size}`);
			console.log(`    Binary files: ${stats.filesSkipped.binary}`);
			console.log(`    Read errors: ${stats.filesSkipped.error}`);
		}
	} catch (error) {
		console.error(red(`Error: ${error.message}`));
		process.exit(1);
	}
}

// Run the search
const start = performance.now();
search({
	pattern: keywords.join(' '),
	caseSensitive: options.caseSensitive,
	charsBefore: options.contextBefore || options.context || 0,
	charsAfter: options.contextAfter || options.context || 0,
	fileTypes: options.type,
	path: options.path,
	binary: options.binary,
	ignore: options.ignore,
	maxMatches: options.maxMatches,
	quiet: options.quiet,
	stats: options.stats,
	contextBefore: options.contextBefore,
	contextAfter: options.contextAfter,
	context: options.context,
	linesBefore: options.linesBefore,
	linesAfter: options.linesAfter,
	lines: options.lines,
}).then(() => {
	if (!options.quiet && !options.json) {
		const end = performance.now();
		console.log(dim(`\nSearch completed in ${(end - start).toFixed(2)}ms`));
	}
}).catch(error => {
	console.error(red(`Error: ${error.message}`));
	process.exit(1);
});