import config from '@app/config';
import { faCommentDots, faPaperPlane } from '@fortawesome/free-regular-svg-icons';
import { faPlusCircle } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { Button, Card, CardBody, CardHeader, Flex, FlexItem, Grid, GridItem, Icon, Panel, PanelMain, PanelMainBody, Stack, StackItem, Text, TextArea, TextContent, TextVariants, Tooltip } from '@patternfly/react-core';
import * as React from 'react';
import orb from '@app/assets/bgimages/orb.svg';
import userAvatar from '@app/assets/bgimages/avatar-user.svg';

const Chat: React.FunctionComponent<{}> = () => {

    type Query = string;
    type Answer = string[];
    type Message = Query | Answer;
    type MessageHistory = Message[];

    const [queryText, setQueryText] = React.useState<Query>('');
    const [answerText, setAnswerText] = React.useState<Answer>([' Hi! I am Parasol Assistant™. How can I help you today?']);
    const [messageHistory, setMessageHistory] = React.useState<MessageHistory>([]);

    const wsUrl = config.backend_api_url.replace(/(http)(s)?(:\/\/.+)\/api/, function (_, http, s, rest) {
        return `ws${s || ''}${rest}/ws`;
    });

    const connection = React.useRef<WebSocket | null>(null);
    const chatBotAnswer = document.getElementById('chatBotAnswer');

    React.useEffect(() => {
        const ws = new WebSocket(wsUrl + '/query') || {};


        ws.onopen = () => {
            console.log('opened ws connection')
        }
        ws.onclose = (e) => {
            console.log('close ws connection: ', e.code, e.reason)
        }

        ws.onmessage = (event) => {
            setAnswerText(answerText => [...answerText, event.data]);
        }

        connection.current = ws;

        // Clean up function
        return () => {
            if (connection.current) {
                connection.current.close();
                console.log('WebSocket connection closed');
            }
        };
    }, [])

    React.useEffect(() => {
        if (chatBotAnswer) {
            chatBotAnswer.scrollTop = chatBotAnswer.scrollHeight;
        }
    }, [answerText]);  // Dependency array


    const sendQueryText = () => {
        if (connection.current?.readyState === WebSocket.OPEN) {
            const previousAnswer = answerText; // Save the previous response, needed because states are updated asynchronously
            setMessageHistory([...messageHistory, previousAnswer, queryText]); // Add the previous response to the message history
            //setMessageHistory([...messageHistory, queryText]); // Add the query to the message history
            // Put the query in a JSON object so that we can add other info later
            let data = {
                query: queryText
            };
            connection.current?.send(JSON.stringify(data)); // Send the query to the server
            setQueryText(''); // Clear the query text
            setAnswerText([]); // Clear the previous response
        };
    }

    const resetMessageHistory = () => {
        setMessageHistory([]);
        setAnswerText(['Hi! I am Parasol Assistant™. How can I help you today?']);
    };

    return (
        <Card isRounded className='chat-card'>
            <CardHeader className='chat-card-header'>
                <TextContent>
                    <Text component={TextVariants.h3} className='chat-card-header-title'><FontAwesomeIcon icon={faCommentDots} />&nbsp;Parasol Assistant&trade;</Text>
                </TextContent>
            </CardHeader>
            <CardBody className='chat-card-body'>
                <Stack>
                    <StackItem isFilled className='chat-bot-answer' id='chatBotAnswer'>
                        <TextContent>
                            {messageHistory.map((message, index) => {
                                const renderMessage = () => {
                                    if (typeof message === 'string') { // If the message is a query
                                        return <Grid className='chat-item'>
                                            <GridItem span={1} className='grid-item-orb'>
                                                <img src={userAvatar} className='user-avatar' />
                                            </GridItem>
                                            <GridItem span={11}>
                                                <Text component={TextVariants.p} className='chat-question-text'>{message}</Text>
                                            </GridItem>
                                        </Grid>
                                    } else { // If the message is a response
                                        return <Grid className='chat-item'>
                                            <GridItem span={1} className='grid-item-orb'>
                                                <img src={orb} className='orb' />
                                            </GridItem>
                                            <GridItem span={11}>
                                                <Text component={TextVariants.p} className='chat-answer-text'>{message.join("")}</Text>
                                            </GridItem>
                                        </Grid>
                                    }
                                };

                                return (
                                    <React.Fragment key={index}>
                                        {renderMessage()}
                                    </React.Fragment>
                                );
                            })}

                            <Grid className='chat-item'>
                                <GridItem span={1} className='grid-item-orb'>
                                    <img src={orb} className='orb' />
                                </GridItem>
                                <GridItem span={11}>
                                    <Text component={TextVariants.p} className='chat-answer-text'>{answerText.join("") != "" && answerText.join("")}</Text>
                                </GridItem>
                            </Grid>
                        </TextContent>
                    </StackItem>
                    <StackItem className='chat-input-panel'>
                        <Panel variant="raised">
                            <PanelMain>
                                <PanelMainBody className='chat-input-panel-body'>
                                    <TextArea
                                        value={queryText}
                                        type="text"
                                        onChange={(_event, queryText) => setQueryText(queryText)}
                                        aria-label="query text input"
                                        placeholder='Ask me anything...'
                                        onKeyPress={event => {
                                            if (event.key === 'Enter') {
                                                event.preventDefault();
                                                sendQueryText();
                                            }
                                        }}
                                    />
                                    <Flex>
                                        <FlexItem>
                                            <Tooltip
                                                content={<div>Start a new chat</div>}
                                            >
                                                <Button variant="link" onClick={resetMessageHistory} aria-label='StartNewChat'><FontAwesomeIcon icon={faPlusCircle} /></Button>
                                            </Tooltip>
                                        </FlexItem>
                                        <FlexItem align={{ default: 'alignRight' }}>
                                            <Tooltip
                                                content={<div>Send your query</div>}
                                            >
                                                <Button variant="link" onClick={sendQueryText} aria-label='SendQuery'><FontAwesomeIcon icon={faPaperPlane} /></Button>
                                            </Tooltip>
                                        </FlexItem>
                                    </Flex>
                                </PanelMainBody>
                            </PanelMain>
                        </Panel>
                    </StackItem>
                    <StackItem>
                        <TextContent>
                            <Text className='chat-disclaimer'>Powered by AI. It may display inaccurate info, so please double-check the responses.</Text>
                        </TextContent>
                    </StackItem>
                </Stack>
            </CardBody>
        </Card >
    );
}

export { Chat };
