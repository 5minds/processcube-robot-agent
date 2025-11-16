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
    it('should render empty fragment when no element is selected', () => {
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

      expect(container.firstChild?.childNodes).toHaveLength(0);
    });

    it('should fetch declaration file on mount', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({ agents: [] });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(props.studio.commands.executeCommand).toHaveBeenCalledWith(
          'bpmn.editor.getDefaultJavaScriptDeclarationFile',
          [props.editorDocument]
        );
      });
    });

    it('should render agent and topic selects', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        const selects = screen.getAllByTestId('pane-property');
        expect(selects.length).toBeGreaterThanOrEqual(2);
      });
    });
  });

  describe('agent selection', () => {
    it('should display available agents', async () => {
      const props = createMockProps();
      const agents = [
        { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        { uuid: '2', name: 'Agent 2', url: 'http://localhost:8081' },
      ];

      mockGetRobotAgents.mockReturnValue({ agents });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Agent')).toBeInTheDocument();
      });
    });

    it('should handle agent change', async () => {
      const props = createMockProps();
      const agents = [
        { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
      ];

      mockGetRobotAgents.mockReturnValue({ agents });
      mockFetchRobots.mockResolvedValue([
        { name: 'Robot 1', topic: 'robot_1' },
      ]);

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        const selects = screen.getAllByTestId('pane-property');
        if (selects.length > 0) {
          fireEvent.change(selects[0], { target: { value: '1' } });
        }
      });
    });

    it('should fetch robots when agent is selected', async () => {
      const props = createMockProps();
      const agents = [
        { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
      ];

      mockGetRobotAgents.mockReturnValue({ agents });
      mockFetchRobots.mockResolvedValue([
        { name: 'Robot 1', topic: 'robot_1' },
      ]);

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(mockFetchRobots).toHaveBeenCalledWith(
          'http://localhost:8080',
          props.studio,
          true
        );
      });
    });

    it('should display robots for selected agent', async () => {
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

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(mockFetchRobots).toHaveBeenCalled();
      });
    });
  });

  describe('robot selection', () => {
    it('should display available robots for selected agent', async () => {
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

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Topic')).toBeInTheDocument();
      });
    });

    it('should handle robot selection', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockFetchRobots.mockResolvedValue([
        { name: 'Robot 1', topic: 'robot_1' },
      ]);

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        const selects = screen.getAllByTestId('pane-property');
        if (selects.length > 1) {
          fireEvent.change(selects[1], { target: { value: 'robot_1' } });

          expect(
            props.editorDocumentModel.elements.setElementProperty
          ).toHaveBeenCalled();
        }
      });
    });
  });

  describe('robot fetch error handling', () => {
    it('should show error notification on fetch failure', async () => {
      const props = createMockProps();

      mockGetRobotAgents.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockFetchRobots.mockRejectedValue(new Error('Connection failed'));

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(props.studio.notifications.open).toHaveBeenCalledWith(
          expect.objectContaining({
            type: 'error',
            source: 'Robot-Agent-Addin',
          }),
          expect.any(Function)
        );
      });
    });

    it('should allow retry on fetch failure', async () => {
      const props = createMockProps();
      let callCount = 0;

      mockGetRobotAgents.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockFetchRobots.mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject(new Error('Connection failed'));
        }
        return Promise.resolve([{ name: 'Robot 1', topic: 'robot_1' }]);
      });

      render(<PropertiesRobotTaskPaneContent {...props} />);

      await waitFor(() => {
        expect(props.studio.notifications.open).toHaveBeenCalled();
      });

      // Simulate retry action
      const lastCall = props.studio.notifications.open.mock.calls[
        props.studio.notifications.open.mock.calls.length - 1
      ];
      if (lastCall) {
        const callback = lastCall[1];
        callback({ action: 'retry' });

        // Should attempt fetch again
        expect(mockFetchRobots).toHaveBeenCalledTimes(2);
      }
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