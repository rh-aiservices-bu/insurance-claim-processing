import * as React from 'react';
import axios from 'axios';
import { Page, PageSection, Title, Card, Label, TextContent, Text, TextVariants, Accordion, AccordionContent, AccordionItem, AccordionToggle, Flex, FlexItem, Button } from '@patternfly/react-core';
import { Table, Thead, Tr, Th, Tbody, Td, TableText } from '@patternfly/react-table';
import { Grid, GridItem } from '@patternfly/react-core';
import { Link, useParams } from 'react-router-dom';
import { Breadcrumb, BreadcrumbItem } from '@patternfly/react-core';
import { ImageCarousel } from '../ImageCarousel/ImageCarousel';
import config from '@app/config';

interface ClaimDetailProps { }

const ClaimDetail: React.FunctionComponent<ClaimDetailProps> = () => {
    const { claim_id } = useParams<{ claim_id: string }>();
    const [claim, setClaim] = React.useState<any>({});
    const [expanded, setExpanded] = React.useState(['']);

    const toggle = (id) => {
        const index = expanded.indexOf(id);
        const newExpanded: string[] =
            index >= 0 ? [...expanded.slice(0, index), ...expanded.slice(index + 1, expanded.length)] : [...expanded, id];
        setExpanded(newExpanded);
    };

    const [claimNumber, setClaimNumber] = React.useState<number>(0);

    React.useEffect(() => {
        axios.get(config.backend_api_url + `/db/claims/${claim_id}`).then((response) => {
            setClaim(response.data);
        });

        axios.get(config.backend_api_url + '/db/claims').then((response) => {
            setClaimNumber(response.data.length);
        });
    }, [claim_id]);

    return (
        <Page>
            <Breadcrumb ouiaId="BasicBreadcrumb" className='simple-padding'>
                <BreadcrumbItem to="/ClaimsList">Claims List</BreadcrumbItem>
                <BreadcrumbItem isActive>{`Claim ${claim_id}`}</BreadcrumbItem>
            </Breadcrumb>
            <PageSection>
                <Flex justifyContent={{ default: 'justifyContentSpaceBetween' }} className='simple-padding'>
                    <FlexItem>
                        <Title headingLevel="h1" size="2xl">{`Claim ${claim_id}`}</Title>
                    </FlexItem>
                    <Flex>
                        {claim_id !== '1' && (
                            <FlexItem>
                                <Link to={`/ClaimDetail/${Number(claim_id) - 1}`}><Button variant="secondary">&lt;&lt;Previous claim</Button></Link>
                            </FlexItem>
                        )}
                        {claim_id !== claimNumber.toString() && (
                            <FlexItem>
                                <Link to={`/ClaimDetail/${Number(claim_id) + 1}`}><Button variant="secondary">&gt;&gt;Next claim</Button></Link>
                            </FlexItem>
                        )}
                    </Flex>
                </Flex>
                <Card>
                    <Grid hasGutter className='simple-padding'>
                        <GridItem span={8}>
                            <TextContent>
                                <Text component={TextVariants.h3}>Subject:</Text>
                                {claim.subject}
                                <Text component={TextVariants.h3}>Summary:</Text>
                                {claim.summary}
                                <Text component={TextVariants.h3}>Customer sentiment:</Text>
                                {claim.sentiment}
                            </TextContent>
                        </GridItem>
                        <GridItem span={4} >
                            <TextContent>
                                <Text component={TextVariants.h3}>Date and time of the event:</Text>
                                {claim.time ? claim.time : 'No date or time specified'}
                                <Text component={TextVariants.h3}>Location of event:</Text>
                                {claim.location ? claim.location : 'No location specified'}
                                <Text component={TextVariants.h3}>Images:</Text>
                                {(claim && claim.processed_images) ? <ImageCarousel images={claim.processed_images}/> : 'No images attached'}
                            </TextContent>
                        </GridItem>
                        <GridItem span={12}>
                            <Accordion isBordered asDefinitionList={false}>
                                <AccordionItem>
                                    <AccordionToggle
                                        onClick={() => toggle('claim-toggle1')}
                                        isExpanded={expanded.includes('claim-toggle1')}
                                        id="claim-toggle1">
                                        Original claim content
                                    </AccordionToggle>
                                    <AccordionContent id="claim-toggle1" isHidden={!expanded.includes('claim-toggle1')}>
                                        <TextContent>
                                            <Text component={TextVariants.h3}>Subject:</Text>
                                            {claim.subject}
                                            <Text component={TextVariants.h3}>Body:</Text>
                                            <div className='display-linebreak'>{claim.body}</div>
                                            <Text component={TextVariants.h3}>Attached images:</Text>
                                            {claim && claim.original_images && <ImageCarousel images={claim.original_images} />}
                                        </TextContent>
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </GridItem>
                    </Grid>
                </Card>
            </PageSection>
        </Page>
    );
}

export { ClaimDetail };