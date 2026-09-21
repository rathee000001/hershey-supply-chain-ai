import Link from "next/link";
import {ArrowRight} from "lucide-react";
import type {EnrichedArtifacts} from "@/lib/hershey/enrichedArtifacts";
import StoryObject from "./StoryObject";
import {formatCents} from "./IngredientPanels";
export default function HomePeopleStory({data}:{data:EnrichedArtifacts}){
 const observations=data.calculationDetails.verified_retailers;
 const prices=observations.map(item=>item.price_cents_per_bar);
 const retailerNames:Record<string,string>={cvs:"CVS",target:"Target",walgreens:"Walgreens",walmart:"Walmart"};
 const names=observations.map(item=>retailerNames[item.retailer.toLowerCase()]||item.retailer).join(", ");
 return <div className="ih-customer-story"><div className="ih-customer-lead"><div className="ih-customer-art" role="img" aria-label="Illustration of two shoppers with a grocery bag"><StoryObject name="people"/></div><div><p className="ih-card-kicker">AT THE END OF THE JOURNEY</p><h4>A familiar bar.<br/>A choice on the shelf.</h4><p>Ingredients, manufacturing, packaging and delivery come together in the product a shopper picks up. The wrapper tells them what is inside; the shelf price tells them what they pay.</p></div></div><div className="ih-customer-facts"><div><strong>One product, different prices</strong><p>The research includes this bar at {names}. {prices.length>0&&<>Recorded prices range from {formatCents(Math.min(...prices))} to {formatCents(Math.max(...prices))} per bar.</>}</p></div><div><strong>More than the cost to make it</strong><p>A shelf price is different from the estimated cost of ingredients, packaging, manufacturing and transport. Explore both to understand the comparison.</p></div></div><Link href="/cost-model" className="ih-inline-action">Explore what goes into the price <ArrowRight size={16}/></Link><p className="ih-fine">Illustrative shoppers; no individual purchases are tracked. Saved prices are not live quotes, and the price–cost gap is not a profit figure.</p></div>;
}
