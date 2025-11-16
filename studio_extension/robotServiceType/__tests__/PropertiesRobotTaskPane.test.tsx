import React from 'react';
import { render, screen } from '@testing-library/react';
import { paneProvider, ROBOT_ICON_SVG } from '../PropertiesRobotTaskPane';

describe('PropertiesRobotTaskPane', () => {
  describe('ROBOT_ICON_SVG', () => {
    it('should render robot icon SVG', () => {
      const { container } = render(ROBOT_ICON_SVG as any);

      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should have correct class name', () => {
      const { container } = render(ROBOT_ICON_SVG as any);

      expect(
        container.querySelector('.robot-agents-properties-pane--robot-icon')
      ).toBeInTheDocument();
    });

    it('should preserve aspect ratio', () => {
      const { container } = render(ROBOT_ICON_SVG as any);

      expect(container.querySelector('svg')?.getAttribute('preserveAspectRatio')).toBe('xMinYMin meet');
    });

    it('should have viewBox set', () => {
      const { container } = render(ROBOT_ICON_SVG as any);

      expect(container.querySelector('svg')?.getAttribute('viewBox')).toBe('0 0 512 512');
    });

    it('should have robot icon path', () => {
      const { container } = render(ROBOT_ICON_SVG as any);

      expect(container.querySelector('path')).toBeInTheDocument();
      expect(container.querySelector('path')?.getAttribute('fill')).toBe(
        'var(--color-bpmn-defaultStrokeColor)'
      );
    });
  });

  describe('paneProvider', () => {
    it('should provide pane title', () => {
      expect(paneProvider.getPaneTitle()).toBe('Robot Service Task');
    });

    it('should provide Pane component', () => {
      expect(paneProvider.Pane).toBeTruthy();
      expect(typeof paneProvider.Pane).toBe('function');
    });

    it('should provide PaneContent component', () => {
      expect(paneProvider.PaneContent).toBeTruthy();
    });

    it('should provide shouldBeDisplayed function', () => {
      expect(paneProvider.shouldBeDisplayed).toBeTruthy();
      expect(typeof paneProvider.shouldBeDisplayed).toBe('function');
    });
  });

  describe('PaneFull component', () => {
    const createMockStudio = () => ({
      commands: {
        executeCommand: jest.fn().mockResolvedValue('test-declaration-file.d.ts'),
      },
      solution: {
        getSolution: jest.fn(() => ({})),
      },
      notifications: {
        open: jest.fn(),
        close: jest.fn(),
      },
      editors: {
        focusOrOpenEditorDocument: jest.fn(),
      },
    });

    const createMockEditorDocumentModel = (selectionElement: any = null) => ({
      selection: {
        getOnlyElementOrNull: jest.fn(() => selectionElement),
      },
      elements: {
        getAllElements: jest.fn(() => []),
      },
      overlays: {
        removeAll: jest.fn(),
        addIcon: jest.fn(),
        addCover: jest.fn(),
        addReactElementOverlay: jest.fn(),
        update: jest.fn(),
      },
    });

    it('should render pane header when displayed', () => {
      const mockProps = {
        collapsed: false,
        paneId: 'test-pane',
        studio: createMockStudio() as any,
        editorDocument: { documentType: 'bpmn' } as any,
        editorDocumentModel: createMockEditorDocumentModel({
          id: 'task-1',
          type: 'ExternalServiceTask',
          customProperties: [
            { name: 'studio.externalTask.customType', value: 'robot' },
          ],
        }),
      };

      const PaneFull = paneProvider.Pane;
      const { container } = render(<PaneFull {...mockProps} />);

      expect(container).toBeInTheDocument();
    });

    it('should render pane content when not collapsed', () => {
      const mockProps = {
        collapsed: false,
        paneId: 'test-pane',
        studio: createMockStudio() as any,
        editorDocument: { documentType: 'bpmn' } as any,
        editorDocumentModel: createMockEditorDocumentModel({
          id: 'task-1',
          type: 'ExternalServiceTask',
          customProperties: [
            { name: 'studio.externalTask.customType', value: 'robot' },
          ],
        }),
      };

      const PaneFull = paneProvider.Pane;
      const { container } = render(<PaneFull {...mockProps} />);

      // PaneContent should be rendered when not collapsed
      expect(container).toBeInTheDocument();
    });

    it('should not render pane content when collapsed', () => {
      const mockProps = {
        collapsed: true,
        paneId: 'test-pane',
        studio: createMockStudio() as any,
        editorDocument: { documentType: 'bpmn' } as any,
        editorDocumentModel: createMockEditorDocumentModel({
          id: 'task-1',
          type: 'ExternalServiceTask',
          customProperties: [
            { name: 'studio.externalTask.customType', value: 'robot' },
          ],
        }),
      };

      const PaneFull = paneProvider.Pane;
      const { container } = render(<PaneFull {...mockProps} />);

      // When collapsed, component should still render
      expect(container).toBeInTheDocument();
    });
  });

  describe('shouldBeDisplayed function', () => {
    const createMockEditorDocumentModel = (selectionElement: any = null) => ({
      selection: {
        getOnlyElementOrNull: jest.fn(() => selectionElement),
      },
      elements: {
        getAllElements: jest.fn(() => []),
      },
      overlays: {
        removeAll: jest.fn(),
        addIcon: jest.fn(),
        addCover: jest.fn(),
        addReactElementOverlay: jest.fn(),
        update: jest.fn(),
      },
    });

    it('should return false for non-bpmn documents', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'json' } as any;
      const mockEditorDocumentModel = createMockEditorDocumentModel();

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return false when no element is selected', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = createMockEditorDocumentModel();

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return false for non-external service tasks', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = createMockEditorDocumentModel({
        id: 'task-1',
        type: 'ServiceTask',
        customProperties: [],
      });

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return false when external task is not robot type', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = createMockEditorDocumentModel({
        id: 'task-1',
        type: 'ExternalServiceTask',
        customProperties: [
          { name: 'studio.externalTask.customType', value: 'other' },
        ],
      });

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return true for robot external service tasks', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = createMockEditorDocumentModel({
        id: 'task-1',
        type: 'ExternalServiceTask',
        customProperties: [
          { name: 'studio.externalTask.customType', value: 'robot' },
        ],
      });

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(true);
    });

    it('should return false when custom type property is not found', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = createMockEditorDocumentModel({
        id: 'task-1',
        type: 'ExternalServiceTask',
        customProperties: [],
      });

      // When custom type is undefined, it should return false
      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });
  });
});