import * as monaco from 'monaco-editor'

// Define language configurations
export const configureMonacoLanguages = () => {
  // Configure Markdown language support
  monaco.languages.register({ id: 'markdown' })
  
  // Set up Markdown language configuration
  monaco.languages.setLanguageConfiguration('markdown', {
    comments: {
      blockComment: ['<!--', '-->']
    },
    brackets: [
      ['[', ']'],
      ['(', ')'],
      ['{', '}']
    ],
    autoClosingPairs: [
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '{', close: '}' },
      { open: '`', close: '`' },
      { open: '*', close: '*' },
      { open: '_', close: '_' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ],
    surroundingPairs: [
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '{', close: '}' },
      { open: '`', close: '`' },
      { open: '*', close: '*' },
      { open: '_', close: '_' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ]
  })

  // Set up Markdown tokenization (basic Monarch grammar)
  monaco.languages.setMonarchTokensProvider('markdown', {
    tokenizer: {
      root: [
        // Headers
        [/^#{1,6}\s.*$/, 'markup.heading'],
        
        // Bold
        [/\*\*([^*]|\*(?!\*))*\*\*/, 'markup.bold'],
        [/__([^_]|_(?!_))*__/, 'markup.bold'],
        
        // Italic
        [/\*([^*]|\*\*)*\*/, 'markup.italic'],
        [/_([^_]|__)*_/, 'markup.italic'],
        
        // Code blocks
        [/```[\s\S]*?```/, 'markup.code.block'],
        [/`[^`]*`/, 'markup.code.inline'],
        
        // Links
        [/\[([^\]]*)\]\(([^)]*)\)/, 'markup.link'],
        [/\[([^\]]*)\]\[([^\]]*)\]/, 'markup.link'],
        
        // Lists
        [/^\s*[-*+]\s/, 'markup.list'],
        [/^\s*\d+\.\s/, 'markup.list'],
        
        // Blockquotes
        [/^\s*>.*$/, 'markup.quote'],
        
        // Horizontal rules
        [/^\s*[-*_]{3,}\s*$/, 'markup.hr']
      ]
    }
  })

  // Configure JSON language (already built-in, just enhance)
  monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
    validate: true,
    allowComments: false,
    schemas: [
      {
        uri: 'http://myserver/flow-config-schema.json',
        fileMatch: ['**/flow.json'],
        schema: {
          type: 'object',
          properties: {
            version: { type: 'string' },
            accounts: {
              type: 'object',
              additionalProperties: {
                type: 'object',
                properties: {
                  address: { type: 'string' },
                  key: { type: 'string' }
                }
              }
            },
            contracts: {
              type: 'object',
              additionalProperties: {
                type: 'object',
                properties: {
                  source: { type: 'string' },
                  aliases: {
                    type: 'object',
                    additionalProperties: { type: 'string' }
                  }
                }
              }
            },
            networks: {
              type: 'object',
              additionalProperties: {
                type: 'object',
                properties: {
                  host: { type: 'string' },
                  port: { type: 'number' }
                }
              }
            },
            deployments: {
              type: 'object',
              additionalProperties: {
                type: 'object',
                additionalProperties: {
                  type: 'array',
                  items: { type: 'string' }
                }
              }
            }
          }
        }
      }
    ]
  })

  // Register Cadence language
  monaco.languages.register({ id: 'cadence' })
  
  // Set up Cadence language configuration
  monaco.languages.setLanguageConfiguration('cadence', {
    comments: {
      lineComment: '//',
      blockComment: ['/*', '*/']
    },
    brackets: [
      ['{', '}'],
      ['[', ']'],
      ['(', ')']
    ],
    autoClosingPairs: [
      { open: '{', close: '}' },
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ],
    surroundingPairs: [
      { open: '{', close: '}' },
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ],
    indentationRules: {
      increaseIndentPattern: /^((?!\/\/).)*((\{[^}"'`]*)|(\([^)"'`]*)|(\[[^\]"'`]*))$/,
      decreaseIndentPattern: /^((?!.*?\/\*).*)*(\}|\)|\])/
    }
  })

  // Set up Cadence tokenization (Monarch grammar based on Cadence syntax)
  monaco.languages.setMonarchTokensProvider('cadence', {
    keywords: [
      'access', 'account', 'all', 'as', 'auth', 'break', 'case', 'catch', 'continue',
      'contract', 'create', 'default', 'destroy', 'else', 'emit', 'enum', 'event',
      'execute', 'export', 'extends', 'for', 'from', 'fun', 'if', 'import', 'in',
      'init', 'interface', 'let', 'loop', 'panic', 'post', 'pre', 'prepare', 'priv',
      'pub', 'resource', 'return', 'self', 'struct', 'switch', 'transaction', 'try',
      'var', 'view', 'while'
    ],
    
    typeKeywords: [
      'AnyResource', 'AnyStruct', 'Bool', 'Character', 'Int', 'Int8', 'Int16', 'Int32',
      'Int64', 'Int128', 'Int256', 'UInt', 'UInt8', 'UInt16', 'UInt32', 'UInt64',
      'UInt128', 'UInt256', 'Word8', 'Word16', 'Word32', 'Word64', 'Fix64', 'UFix64',
      'String', 'Address', 'Path', 'StoragePath', 'CapabilityPath', 'PublicPath',
      'PrivatePath', 'AuthAccount', 'PublicAccount', 'DeployedContract', 'Capability'
    ],

    operators: [
      '=', '>', '<', '!', '~', '?', ':', '==', '<=', '>=', '!=',
      '&&', '||', '++', '--', '+', '-', '*', '/', '&', '|', '^', '%',
      '<<', '>>', '>>>', '+=', '-=', '*=', '/=', '&=', '|=', '^=',
      '%=', '<<=', '>>=', '>>>='
    ],

    symbols: /[=><!~?:&|+\-*\/\^%]+/,

    tokenizer: {
      root: [
        // Identifiers and keywords
        [/[a-z_$][\w$]*/, {
          cases: {
            '@typeKeywords': 'type',
            '@keywords': 'keyword',
            '@default': 'identifier'
          }
        }],
        [/[A-Z][\w\$]*/, 'type.identifier'],

        // Whitespace
        { include: '@whitespace' },

        // Delimiters and operators
        [/[{}()\[\]]/, '@brackets'],
        [/[<>](?!@symbols)/, '@brackets'],
        [/@symbols/, {
          cases: {
            '@operators': 'operator',
            '@default': ''
          }
        }],

        // Numbers
        [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
        [/0[xX][0-9a-fA-F]+/, 'number.hex'],
        [/\d+/, 'number'],

        // Delimiter: after number because of .\d floats
        [/[;,.]/, 'delimiter'],

        // Strings
        [/"([^"\\]|\\.)*$/, 'string.invalid'],
        [/"/, { token: 'string.quote', bracket: '@open', next: '@string' }],

        // Characters
        [/'[^\\']'/, 'string'],
        [/(')(@escapes)(')/, ['string', 'string.escape', 'string']],
        [/'/, 'string.invalid']
      ],

      comment: [
        [/[^\/*]+/, 'comment'],
        [/\/\*/, 'comment', '@push'],
        ["\\*/", 'comment', '@pop'],
        [/[\/*]/, 'comment']
      ],

      string: [
        [/[^\\"]+/, 'string'],
        [/@escapes/, 'string.escape'],
        [/\\./, 'string.escape.invalid'],
        [/"/, { token: 'string.quote', bracket: '@close', next: '@pop' }]
      ],

      whitespace: [
        [/[ \t\r\n]+/, 'white'],
        [/\/\*/, 'comment', '@comment'],
        [/\/\/.*$/, 'comment'],
      ],
    },

    escapes: /\\(?:[abfnrtv\\"']|x[0-9A-Fa-f]{1,4}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,
  })

  // Set up completion providers for Cadence
  monaco.languages.registerCompletionItemProvider('cadence', {
    provideCompletionItems: (model, position, context, token) => {
      const word = model.getWordUntilPosition(position)
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn
      }

      const suggestions: monaco.languages.CompletionItem[] = [
        // Keywords
        ...['access', 'account', 'all', 'as', 'auth', 'break', 'case', 'catch', 'continue',
          'contract', 'create', 'default', 'destroy', 'else', 'emit', 'enum', 'event',
          'execute', 'export', 'extends', 'for', 'from', 'fun', 'if', 'import', 'in',
          'init', 'interface', 'let', 'loop', 'panic', 'post', 'pre', 'prepare', 'priv',
          'pub', 'resource', 'return', 'self', 'struct', 'switch', 'transaction', 'try',
          'var', 'view', 'while'].map(keyword => ({
            label: keyword,
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: keyword,
            range: range
          })),
        
        // Types
        ...['AnyResource', 'AnyStruct', 'Bool', 'Character', 'Int', 'Int8', 'Int16', 'Int32',
          'Int64', 'Int128', 'Int256', 'UInt', 'UInt8', 'UInt16', 'UInt32', 'UInt64',
          'UInt128', 'UInt256', 'Word8', 'Word16', 'Word32', 'Word64', 'Fix64', 'UFix64',
          'String', 'Address', 'Path', 'StoragePath', 'CapabilityPath', 'PublicPath',
          'PrivatePath', 'AuthAccount', 'PublicAccount', 'DeployedContract', 'Capability'].map(type => ({
            label: type,
            kind: monaco.languages.CompletionItemKind.Class,
            insertText: type,
            range: range
          })),

        // Common snippets
        {
          label: 'contract',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'contract ${1:ContractName} {\n\t${2:// Contract body}\n}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Create a new contract',
          range: range
        },
        {
          label: 'resource',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'resource ${1:ResourceName} {\n\t${2:// Resource body}\n}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Create a new resource',
          range: range
        },
        {
          label: 'function',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'pub fun ${1:functionName}(${2:parameters}): ${3:ReturnType} {\n\t${4:// Function body}\n}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Create a new function',
          range: range
        },
        {
          label: 'transaction',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'transaction(${1:parameters}) {\n\tprepare(${2:signer}: AuthAccount) {\n\t\t${3:// Preparation phase}\n\t}\n\n\texecute {\n\t\t${4:// Execution phase}\n\t}\n}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Create a new transaction',
          range: range
        }
      ]

      return { 
        suggestions,
        incomplete: false
      }
    }
  })
}

// Helper function to get the appropriate language for a file
export const getLanguageFromFileName = (fileName: string): string => {
  const extension = fileName.split('.').pop()?.toLowerCase()
  
  switch (extension) {
    case 'md':
    case 'markdown':
      return 'markdown'
    case 'json':
      return 'json'
    case 'cdc':
      return 'cadence'
    case 'js':
    case 'jsx':
      return 'javascript'
    case 'ts':
    case 'tsx':
      return 'typescript'
    case 'html':
      return 'html'
    case 'css':
      return 'css'
    case 'yaml':
    case 'yml':
      return 'yaml'
    default:
      return 'plaintext'
  }
}

// Enhanced editor options for better experience
export const getEditorOptions = (language: string): monaco.editor.IStandaloneEditorConstructionOptions => {
  const baseOptions: monaco.editor.IStandaloneEditorConstructionOptions = {
    theme: 'vs-dark',
    fontSize: 14,
    lineHeight: 20,
    fontFamily: "'Fira Code', 'Cascadia Code', 'JetBrains Mono', 'SF Mono', Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
    fontLigatures: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    insertSpaces: true,
    wordWrap: 'on',
    lineNumbers: 'on',
    renderLineHighlight: 'line',
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    glyphMargin: true,
    folding: true,
    foldingHighlight: true,
    showFoldingControls: 'mouseover',
    matchBrackets: 'always',
    renderWhitespace: 'selection',
    contextmenu: true,
    mouseWheelZoom: true,
    multiCursorModifier: 'alt',
    accessibilitySupport: 'auto'
  }

  // Language-specific enhancements
  switch (language) {
    case 'markdown':
      return {
        ...baseOptions,
        wordWrap: 'on',
        lineNumbers: 'off',
        folding: true,
        renderLineHighlight: 'none'
      }
    case 'json':
      return {
        ...baseOptions,
        formatOnPaste: true,
        formatOnType: true
      }
    case 'cadence':
      return {
        ...baseOptions,
        suggest: {
          showKeywords: true,
          showSnippets: true,
          showFunctions: true,
          showConstructors: true,
          showFields: true,
          showVariables: true,
          showClasses: true,
          showStructs: true,
          showInterfaces: true,
          showModules: true,
          showProperties: true,
          showEvents: true,
          showOperators: true,
          showUnits: true,
          showValues: true,
          showConstants: true,
          showEnums: true,
          showEnumMembers: true,
          showColors: true,
          showFiles: true,
          showReferences: true,
          showFolders: true,
          showTypeParameters: true,
          showIssues: true,
          showUsers: true,
          showWords: true
        }
      }
    default:
      return baseOptions
  }
}