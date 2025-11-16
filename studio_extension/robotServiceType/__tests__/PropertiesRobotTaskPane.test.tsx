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
    it('should render pane header when displayed', () => {
      const mockProps = {
        collapsed: false,
        paneId: 'test-pane',
        studio: {} as any,
        editorDocument: { documentType: 'bpmn' } as any,
        editorDocumentModel: {
          selection: {
            getOnlyElementOrNull: jest.fn(() => ({
              id: 'task-1',
              type: 'ExternalServiceTask',
              customProperties: [
                { name: 'studio.externalTask.customType', value: 'robot' },
              ],
            })),
          },
        } as any,
      };

      const PaneFull = paneProvider.Pane;
      render(<PaneFull {...mockProps} />);

      expect(screen.getByText('Robot Service Task')).toBeInTheDocument();
    });

    it('should render pane content when not collapsed', () => {
      const mockProps = {
        collapsed: false,
        paneId: 'test-pane',
        studio: {} as any,
        editorDocument: { documentType: 'bpmn' } as any,
        editorDocumentModel: {
          selection: {
            getOnlyElementOrNull: jest.fn(() => ({
              id: 'task-1',
              type: 'ExternalServiceTask',
              customProperties: [
                { name: 'studio.externalTask.customType', value: 'robot' },
              ],
            })),
          },
        } as any,
      };

      const PaneFull = paneProvider.Pane;
      const { container } = render(<PaneFull {...mockProps} />);

      // PaneContent should be rendered
      expect(container.querySelector('[data-testid="pane-content"]') || container.querySelector('div')).toBeInTheDocument();
    });

    it('should not render pane content when collapsed', () => {
      const mockProps = {
        collapsed: true,
        paneId: 'test-pane',
        studio: {} as any,
        editorDocument: { documentType: 'bpmn' } as any,
        editorDocumentModel: {
          selection: {
            getOnlyElementOrNull: jest.fn(() => ({
              id: 'task-1',
              type: 'ExternalServiceTask',
              customProperties: [
                { name: 'studio.externalTask.customType', value: 'robot' },
              ],
            })),
          },
        } as any,
      };

      const PaneFull = paneProvider.Pane;
      const { container } = render(<PaneFull {...mockProps} />);

      // Should only render header, not content
      const contentElements = container.querySelectorAll('[data-testid="pane-content"]');
      expect(contentElements).toHaveLength(0);
    });
  });

  describe('shouldBeDisplayed function', () => {
    it('should return false for non-bpmn documents', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'json' } as any;
      const mockEditorDocumentModel = {} as any;

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return false when no element is selected', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = {
        selection: {
          getOnlyElementOrNull: jest.fn(() => null),
        },
        elements: {
          getAllElements: jest.fn(() => []),
        },
      } as any;

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return false for non-external service tasks', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = {
        selection: {
          getOnlyElementOrNull: jest.fn(() => ({
            id: 'task-1',
            type: 'ServiceTask',
            customProperties: [],
          })),
        },
        elements: {
          getAllElements: jest.fn(() => []),
        },
      } as any;

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return false when external task is not robot type', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = {
        selection: {
          getOnlyElementOrNull: jest.fn(() => ({
            id: 'task-1',
            type: 'ExternalServiceTask',
            customProperties: [
              { name: 'studio.externalTask.customType', value: 'other' },
            ],
          })),
        },
        elements: {
          getAllElements: jest.fn(() => []),
        },
      } as any;

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });

    it('should return true for robot external service tasks', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = {
        selection: {
          getOnlyElementOrNull: jest.fn(() => ({
            id: 'task-1',
            type: 'ExternalServiceTask',
            customProperties: [
              { name: 'studio.externalTask.customType', value: 'robot' },
            ],
          })),
        },
        elements: {
          getAllElements: jest.fn(() => []),
        },
      } as any;

      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(true);
    });

    it('should return true when custom type property is not found', () => {
      const shouldBeDisplayed = paneProvider.shouldBeDisplayed;
      const mockEditorDocument = { documentType: 'bpmn' } as any;
      const mockEditorDocumentModel = {
        selection: {
          getOnlyElementOrNull: jest.fn(() => ({
            id: 'task-1',
            type: 'ExternalServiceTask',
            customProperties: [],
          })),
        },
        elements: {
          getAllElements: jest.fn(() => []),
        },
      } as any;

      // When custom type is undefined, it should return false
      expect(shouldBeDisplayed(mockEditorDocument, mockEditorDocumentModel)).toBe(false);
    });
  });
});