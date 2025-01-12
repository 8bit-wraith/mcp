#!/usr/bin/env node

// GAK - Global Awesome Keywords
// A context-aware search tool that integrates with our MCP system

import { program } from 'commander';
import chalk from 'chalk';
import { readFileSync, statSync } from 'fs';
import { join, relative, sep, dirname } from 'path';
import { fileURLToPath } from 'url';
import { globbySync } from 'globby';
import isTextPath from 'is-text-path';
import prettyBytes from 'pretty-bytes';
import fs from 'fs/promises';
import ora from 'ora';

// Import our context system
import { ContextStore } from '../../core/context_store.js';
import { GitContextBuilder } from '../git_context_builder.js';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const isWindows = process.platform === 'win32';

// ... [rest of the original GAK code] ...

// Enhance search with context awareness
async function searchWithContext(options) {
    const contextStore = new ContextStore();
    const gitContext = new GitContextBuilder();
    
    // Initialize context store
    await contextStore.initialize();
    
    // Add context awareness to search results
    const searchResults = await search(options);
    
    // Store search context
    await contextStore.storeSearchContext({
        timestamp: new Date(),
        keywords: options.pattern.split(' '),
        results: searchResults,
        metadata: {
            filesSearched: stats.filesSearched,
            matchesFound: stats.matchesFound,
            duration: Date.now() - stats.startTime
        }
    });
    
    // Find similar searches
    const similarSearches = await contextStore.findSimilarSearches(options.pattern);
    
    if (similarSearches.length > 0) {
        console.log('\n🔍 Similar searches from history:');
        for (const search of similarSearches) {
            console.log(`  ${chalk.blue(search.keywords.join(' '))} - ${chalk.gray(search.timestamp)}`);
        }
    }
    
    return searchResults;
}

// Export for use in other parts of MCP
export { searchWithContext, search };

// CLI entry point
if (import.meta.url === fileURLToPath(import.meta.url)) {
    program.parse();
    searchWithContext(program.opts());
} 