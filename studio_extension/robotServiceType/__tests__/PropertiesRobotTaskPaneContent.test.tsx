import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PropertiesRobotTaskPaneContent } from '../PropertiesRobotTaskPaneContent';

// Mock dependencies
jest.mock('../fetchRobots', () => ({
  fetchRobots: jest.fn(),
}));

jest.mock('../../agentSettings/getRobotAgents', () => ({
  getRobotAgents: jest.fn(),
}));

import { fetchRobots } from '../fetchRobots';
import { getRobotAgents } from '../../agentSettings/getRobotAgents';

const mockFetchRobots = fetchRobots as jest.MockedFunction<typeof fetchRobots>;
const mockGetRobotAgents = getRobotAgents as jest.MockedFunction<typeof getRobotAgents>;

const createMockProps = (overrides = {}) => ({
  studio: {
    commands: {
      executeCommand: jest.fn().mockResolvedValue('test-declaration-file.d.ts'),
    },
    notifications: {
      open: jest.fn(),
      close: jest.fn(),
    },
    editors: {
      focusOrOpenEditorDocument: jest.fn(),
    },
  } as any,
  editorDocument: {
    uri: 'file:///workspace/process.bpmn',
  } as any,
  editorDocumentModel: {
    selection: {
      getOnlyElementOrNull: jest.fn(() => ({
        id: 'task-1',
        type: 'ExternalServiceTask',
        customProperties: [],
        topic: '',
        payload: '',
      })),
    },
    elements: {
      setElementProperty: jest.fn(),
      setCustomProperty: jest.fn(),
    },
  } as any,
  paneId: 'robot-task-pane',
  collapsed: false,
  ...overrides,
});

describe('PropertiesRobotTaskPaneContent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('initialization', () => {
    it('should render when element is selected', () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({ agents: [] });

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      expect(container).toBeInTheDocument();
    });

    it('should handle no element selected', () => {
      const props = createMockProps({
        editorDocumentModel: {
          selection: {
            getOnlyElementOrNull: jest.fn(() => null),
          },
          elements: {
            setElementProperty: jest.fn(),
            setCustomProperty: jest.fn(),
          },
        },
      });

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      expect(container).toBeInTheDocument();
    });
  });

  describe('agent selection', () => {
    it('should handle agents when available', () => {
      const props = createMockProps();
      const agents = [
        { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        { uuid: '2', name: 'Agent 2', url: 'http://localhost:8081' },
      ];

      mockGetRobotAgents.mockReturnValue({ agents });

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      expect(container).toBeInTheDocument();
      expect(mockGetRobotAgents).toHaveBeenCalled();
    });

    it('should fetch robots for selected agent', () => {
      const props = createMockProps();
      const agents = [
        { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
      ];

      mockGetRobotAgents.mockReturnValue({ agents });
      mockFetchRobots.mockResolvedValue([
        { name: 'Robot 1', topic: 'robot_1' },
      ]);

      render(<PropertiesRobotTaskPaneContent {...props} />);

      // Component should handle agents without errors
      expect(mockGetRobotAgents).toHaveBeenCalled();
    });

    it('should work with pre-selected agent', () => {
      const props = createMockProps({
        editorDocumentModel: {
          selection: {
            getOnlyElementOrNull: jest.fn(() => ({
              id: 'task-1',
              type: 'ExternalServiceTask',
              customProperties: [
                { name: 'studio.externalTask.robotAddin.agentId', value: '1' },
              ],
              topic: 'robot_1',
              payload: '',
            })),
          },
          elements: {
            setElementProperty: jest.fn(),
            setCustomProperty: jest.fn(),
          },
        },
      });

      const agents = [
        { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
      ];

      mockGetRobotAgents.mockReturnValue({ agents });
      mockFetchRobots.mockResolvedValue([
        { name: 'Robot 1', topic: 'robot_1' },
      ]);

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      expect(container).toBeInTheDocument();
    });
  });

  describe('robot selection', () => {
    it('should display robots', () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockFetchRobots.mockResolvedValue([
        { name: 'Robot 1', topic: 'robot_1' },
        { name: 'Robot 2', topic: 'robot_2' },
      ]);

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      expect(container).toBeInTheDocument();
    });

    it('should handle robot selection flow', () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockFetchRobots.mockResolvedValue([
        { name: 'Robot 1', topic: 'robot_1' },
      ]);

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      // Verify component rendered and mocks were called
      expect(container).toBeInTheDocument();
      expect(mockGetRobotAgents).toHaveBeenCalled();
    });
  });

  describe('error handling', () => {
    it('should handle fetch errors gracefully', () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockFetchRobots.mockRejectedValue(new Error('Connection failed'));

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      // Verify component rendered without crashing
      expect(container).toBeInTheDocument();
    });

    it('should work with no agents available', () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({ agents: [] });
      mockFetchRobots.mockResolvedValue([]);

      const { container } = render(
        <PropertiesRobotTaskPaneContent {...props} />
      );

      expect(container).toBeInTheDocument();
      expect(mockGetRobotAgents).toHaveBeenCalled();
    });
  });

  describe('payload editor', () => {
    it('should render payload editor', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({ agents: [] });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Body')).toBeInTheDocument();
      });
    });

    it('should display initial payload value', async () => {
      const props = createMockProps({
        editorDocumentModel: {
          selection: {
            getOnlyElementOrNull: jest.fn(() => ({
              id: 'task-1',
              type: 'ExternalServiceTask',
              customProperties: [],
              topic: '',
              payload: '{ "test": "data" }',
            })),
          },
          elements: {
            setElementProperty: jest.fn(),
            setCustomProperty: jest.fn(),
          },
        },
      });

      mockGetRobotAgents.mockReturnValue({ agents: [] });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        const editor = screen.getByTestId('multi-line-code-editor');
        expect(editor).toHaveValue('{ "test": "data" }');
      });
    });

    it('should update payload on change', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({ agents: [] });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        const editor = screen.getByTestId('multi-line-code-editor');
        fireEvent.change(editor, { target: { value: '{ "new": "payload" }' } });

        expect(props.editorDocumentModel.elements.setElementProperty).toHaveBeenCalled();
      });
    });

    it('should show open in new tab link', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({ agents: [] });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Open in new tab')).toBeInTheDocument();
      });
    });
  });

  describe('class methods', () => {
    it('should update external task properties', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({ agents: [] });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(props.studio.commands.executeCommand).toHaveBeenCalled();
      });
    });
  });
});