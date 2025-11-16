# TypeScript/React Studio Extension - Migration Guide

## Paket-Updates

| Paket | Alt | Neu | Status |
|-------|-----|-----|--------|
| react | 18.x | 19.x | 🔴 MAJOR |
| react-dom | 18.x | 19.x | 🔴 MAJOR |
| typescript | 5.3.x | 5.9.x | 🟡 MINOR |
| webpack | 5.89.x | 5.102.x | 🟡 PATCH |
| webpack-cli | 5.1.x | 6.x | 🔴 MAJOR |
| eslint | 8.x | 9.x | 🔴 MAJOR |
| @typescript-eslint/* | 6.x | 8.x | 🔴 MAJOR |
| sass | 1.69.x | 1.94.x | 🟡 PATCH |
| css-loader | 6.8.x | 7.1.x | 🟡 MINOR |
| style-loader | 3.3.x | 4.0.x | 🔴 MAJOR |

---

## 1. React 18.x → 19.x - MAJOR BREAKING

### Was hat sich geändert?

**Rendering Behavior:**
```typescript
// Alte Version (18.x)
import ReactDOM from 'react-dom';

ReactDOM.render(
  <App />,
  document.getElementById('root')
);

// Neue Version (19.x)
import { createRoot } from 'react-dom/client';

const root = createRoot(document.getElementById('root')!);
root.render(<App />);
```

**Hooks & State Management:**
```typescript
// Alte Version (18.x)
import { useState } from 'react';

const MyComponent = () => {
  const [state, setState] = useState('initial');

  return <div>{state}</div>;
};

// Neue Version (19.x) - Kann auch automatisch optimiert werden
const MyComponent = () => {
  const [state, setState] = useState('initial');

  return <div>{state}</div>;
  // Automatische Batching und Transitions
};
```

**New Features in React 19:**
- Server Components (Experimental)
- Use Hook für Promises
- Automatic Batching
- Improved Error Boundaries

### Migration Steps

1. **Update React in robotServiceType:**
   ```bash
   cd studio_extension
   npm install react@19 react-dom@19
   ```

2. **Update Entry Point:**
   ```typescript
   // robotServiceType/index.tsx
   import { createRoot } from 'react-dom/client';

   const root = createRoot(document.getElementById('root')!);
   root.render(<App />);
   ```

3. **Test Components:**
   ```bash
   npm run build
   npm run lint
   ```

### Checklist

- [ ] React 19 installiert
- [ ] Entry Points aktualisiert
- [ ] Components getestet
- [ ] TypeScript-Fehler gelöst
- [ ] Build erfolgreich

---

## 2. TypeScript 5.3.x → 5.9.x - MINOR UPDATE

### Was hat sich geändert?

**Neue Features:**
- Bessere Type Inference
- Neue TypeScript Keywords
- Performance Improvements

**Beispiel - bessere Type Guards:**
```typescript
// Alte Version (5.3)
interface Animal {
  type: 'dog' | 'cat';
  name: string;
}

// Neue Version (5.9) - bessere Type Narrowing
type Dog = Animal & { type: 'dog'; breed: string };
type Cat = Animal & { type: 'cat'; color: string };
```

### Migration Steps

1. **TypeScript Update:**
   ```bash
   npm install -D typescript@5.9
   ```

2. **Neuen Compiler checken:**
   ```bash
   npm run lint
   # Überprüfe auf neue Warnungen
   ```

3. **tsconfig.json anpassen (optional):**
   ```json
   {
     "compilerOptions": {
       "target": "ES2020",
       "lib": ["ES2020", "DOM"],
       "strict": true,
       "moduleResolution": "bundler"
     }
   }
   ```

### Checklist

- [ ] TypeScript 5.9 installiert
- [ ] TypeScript-Fehler gelöst
- [ ] Neuer Compiler ausgeführt
- [ ] Build erfolgreich
- [ ] Keine neuen Warnungen

---

## 3. Webpack 5 → 5.102 & webpack-cli 5 → 6 - BREAKING

### Was hat sich geändert?

**webpack-cli Update:**
```bash
# Alte Version (5.x)
webpack-cli --mode production

# Neue Version (6.x) - besseres Argument-Parsing
webpack serve --mode production
```

**webpack Konfiguration:**
```javascript
// webpack.config.js
module.exports = {
  mode: 'production',
  entry: './src/index.ts',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    clean: true  // Neue Option in 5.102+
  },
  optimization: {
    minimize: true,
    usedExports: true
  }
};
```

### Migration Steps

1. **Dependencies aktualisieren:**
   ```bash
   npm install -D webpack@5.102 webpack-cli@6
   ```

2. **webpack.config.js überprüfen:**
   ```bash
   npm run build
   ```

3. **Scripts in package.json prüfen:**
   ```json
   {
     "scripts": {
       "build": "webpack-cli",
       "build:watch": "webpack-cli --watch"
     }
   }
   ```

### Checklist

- [ ] webpack-cli 6 installiert
- [ ] webpack.config.js angepasst
- [ ] Build erfolgreich
- [ ] Keine Deprecation Warnings

---

## 4. ESLint 8.x → 9.x - MAJOR BREAKING

### Was hat sich geändert?

**ESLint Config Format:**
```javascript
// Alte Version (8.x) - .eslintrc.js
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: ['eslint:recommended'],
  rules: {
    'no-console': 'warn'
  }
};

// Neue Version (9.x) - eslint.config.js
import tsParser from '@typescript-eslint/parser';
import js from '@eslint/js';

export default [
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser
    },
    rules: {
      'no-console': 'warn'
    }
  }
];
```

### Migration Steps

1. **ESLint aktualisieren:**
   ```bash
   npm install -D eslint@9 @eslint/js
   ```

2. **eslint.config.js erstellen:**
   ```javascript
   import tsParser from '@typescript-eslint/parser';
   import tsPlugin from '@typescript-eslint/eslint-plugin';
   import reactPlugin from 'eslint-plugin-react';

   export default [
     {
       files: ['**/*.{ts,tsx}'],
       languageOptions: {
         parser: tsParser,
         parserOptions: {
           ecmaVersion: 'latest',
           sourceType: 'module',
           ecmaFeatures: { jsx: true }
         }
       },
       plugins: {
         '@typescript-eslint': tsPlugin,
         react: reactPlugin
       },
       rules: {
         'no-console': 'warn',
         'react/react-in-jsx-scope': 'off'
       }
     }
   ];
   ```

3. **alte .eslintrc.js löschen:**
   ```bash
   rm .eslintrc.js
   ```

4. **Lint testen:**
   ```bash
   npm run lint
   ```

### Checklist

- [ ] ESLint 9 installiert
- [ ] eslint.config.js erstellt
- [ ] alte ESLint Konfiguration gelöscht
- [ ] Lint erfolgreich durchgeführt
- [ ] Keine Fehler oder Warnungen

---

## 5. @typescript-eslint 6.x → 8.x - MAJOR BREAKING

### Was hat sich geändert?

**Parser & Plugin Updates:**
```javascript
// Neue Config-Struktur
import tsPlugin from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';

export default [
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser
    },
    plugins: {
      '@typescript-eslint': tsPlugin
    },
    rules: {
      '@typescript-eslint/explicit-function-return-types': 'warn'
    }
  }
];
```

**Neue Rules:**
- `consistent-type-imports` - Konsistente Type Imports
- `no-unused-vars` - Bessere Variable Detection

### Migration Steps

1. **Dependencies aktualisieren:**
   ```bash
   npm install -D @typescript-eslint/parser@8 @typescript-eslint/eslint-plugin@8
   ```

2. **ESLint Config wie oben erstellen**

3. **Alte Rules durchprüfen und aktualisieren**

### Checklist

- [ ] @typescript-eslint 8 installiert
- [ ] ESLint Config angepasst
- [ ] Neue Rules überprüft
- [ ] Lint erfolgreich

---

## 6. Sonstige Updates (Kompatibel)

### sass 1.69 → 1.94
- Vollständig abwärtskompatibel
- Performance Improvements
- Keine Code-Änderungen nötig

### css-loader 6.8 → 7.1
- Vollständig abwärtskompatibel
- Bessere Module Support
- Keine Code-Änderungen nötig

### style-loader 3.3 → 4.0
- Vollständig abwärtskompatibel
- Performance Improvements
- Keine Code-Änderungen nötig

---

## Testing & Validation

### 1. Build testen
```bash
cd studio_extension
npm install
npm run build
```

### 2. Linting durchführen
```bash
npm run lint
npm run lint-fix  # Auto-Fix where possible
```

### 3. TypeScript Type Checking
```bash
npx tsc --noEmit
```

### 4. Studio Extension testen
```bash
npm run studio
# Überprüfe dass Extension in Studio ladet
```

---

## Success Criteria

✅ Build erfolgreich ohne Fehler
✅ Linting bestätigt (0 Fehler)
✅ TypeScript Types korrekt
✅ Keine Console-Fehler im Studio
✅ UI Components funktionieren
✅ Keine Breaking Changes für Users

---

## Rollback Plan

Falls kritische Issues auftreten:

```bash
# Alte package-lock.json wiederherstellen
git checkout studio_extension/package-lock.json

# Dependencies erneut installieren
cd studio_extension
npm install

# Alte Konfig wiederherstellen
git checkout studio_extension/eslint.config.js
```

---

**Erstellt:** November 2025
**Gültig bis:** Dezember 2025