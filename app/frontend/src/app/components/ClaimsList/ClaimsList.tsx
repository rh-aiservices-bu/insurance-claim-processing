import * as React from 'react';
import axios from 'axios';
import { Label, Card, Page, PageSection, TextContent, Text, TextVariants, Title, Tabs, Tab, Accordion, AccordionItem, AccordionToggle, AccordionContent, Flex, FlexItem } from '@patternfly/react-core';
import { Table, Thead, Tr, Th, Tbody, Td, TableText } from '@patternfly/react-table';
import { ClaimDetail } from '../ClaimDetail/ClaimDetail';
import { Link } from 'react-router-dom';
import { any } from 'prop-types';
import config from '@app/config';

const ClaimsList: React.FunctionComponent = () => {

    const [claims, setClaims] = React.useState([]);

    React.useEffect(() => {
        console.log(config.backend_api_url + '/db/claims')
        axios.get(config.backend_api_url + '/db/claims')
            .then(response => {
                setClaims(response.data);
            })
            .catch(error => {
                console.error(error);
            });
    }, []);

    const renderLabel = (labelText: string) => {
        if (labelText == null || labelText == '') {
            return <Label color="red">Unprocessed</Label>;
        } else {
            return <Label color="green">Processed</Label>;
        }

    };

    const rows = claims.map((claim: any) => ({
        cells: [
            { title: claim.id },
            { title: claim.subject },
            { title: claim.summary }
        ]
    }));

    return (
        <Page>
            <PageSection>
                <Title headingLevel="h1" size="lg">Received Claims</Title>
                <Card component="div">
                    <Table aria-label="Claims list" isStickyHeader>
                        <Thead>
                            <Tr>
                                <Th width={10}>Claim ID</Th>
                                <Th width={70}>Subject</Th>
                                <Th width={10}>Status</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {rows.map((row, rowIndex) => (
                                <Tr key={rowIndex}>
                                    {row.cells.map((cell, cellIndex) => (
                                        <Td key={cellIndex}>{cellIndex === 2 ? renderLabel(cell.title) : <Link to={`/ClaimDetail/${row.cells[0].title}`}>{cell.title}</Link>}</Td>
                                    ))}
                                </Tr>
                            ))}
                        </Tbody>
                    </Table>
                </Card>
            </PageSection>
        </Page>
    )
}

export { ClaimsList };
