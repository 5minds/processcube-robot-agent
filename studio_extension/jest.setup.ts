import '@testing-library/jest-dom';
import React from 'react';

// Mock the @5minds/processcube_studio_sdk module
jest.mock('@5minds/processcube_studio_sdk', () => {
  const React = require('react');
  return {
    Studio: jest.fn(),
    BpmnDocumentModel: jest.fn(),
    EditorDocumentModel: jest.fn(),
    EditorDocument: jest.fn(),
    Pane: (props: any) => React.createElement('div', null, props.children),
    PaneHeader: jest.fn((props: any) => React.createElement('div', null, props.title)),
    PaneHeaderHelpIcon: jest.fn(),
    PaneProvider: jest.fn(),
    PaneBody: (props: any) => React.createElement('div', null, props.children),
    PaneProperty: jest.fn((props: any) =>
      React.createElement(
        'select',
        {
          'data-testid': 'pane-property',
          value: props.value?.value?.uuid || '',
          onChange: (e: any) => {
            const selected = props.options?.find(
              (opt: any) => opt.value.uuid === e.target.value
            );
            props.onChange?.(selected);
          },
        },
        props.options?.map((opt: any) =>
          React.createElement(
            'option',
            { key: opt.value.uuid, value: opt.value.uuid },
            opt.label
          )
        )
      )
    ),
    Editor: (props: any) => React.createElement('div', { className: 'editor' }, props.children),
    EditorContent: (props: any) => React.createElement('div', null, props.children),
    OneLineCodeEditor: jest.fn((props: any) =>
      React.createElement('input', {
        'data-testid': 'one-line-code-editor',
        defaultValue: props.initialValue,
        onChange: (e: any) => props.onChange(e.target.value),
      })
    ),
    MultiLineCodeEditor: jest.fn((props: any) =>
      React.createElement('textarea', {
        'data-testid': 'multi-line-code-editor',
        defaultValue: props.initialValue,
        onChange: (e: any) => props.onChange(e.target.value),
      })
    ),
    RuntimeExpressionHint: jest.fn(),
    SelectOption: jest.fn(),
    getUrlForOpenInNewTab: jest.fn((id: string) => `/open/${id}`),
    assertNotNull: (value: any, message: string) => {
      if (value === null || value === undefined) {
        throw new Error(`Assertion failed: ${message}`);
      }
      return value;
    },
    BpmnElementType: {
      ExternalServiceTask: 'ExternalServiceTask',
    },
  };
});

// Suppress console errors in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});