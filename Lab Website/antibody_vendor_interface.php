<?php

include("pdf_to_text.php");

libxml_use_internal_errors(true);

 if(isset($_GET["vendor"]) == false || isset($_GET["search_text"]) == false) {
       
       RETURN_RESPONSE(0, "missing_query_info");
   }

$VENDOR = $_GET["vendor"];
$SEARCH_TEXT = $_GET["search_text"];


function RETURN_RESPONSE($code, $info, $data = array()){
        
        $RESULT_ARRAY = array();
        $RESULT_ARRAY["success_code"] = $code;
        $RESULT_ARRAY["info"] = $info;
        $RESULT_ARRAY["data"] = $data;
        
        header('Content-Type: application/json');
        echo json_encode($RESULT_ARRAY);
        exit();   
    }



function MULTI_REQUEST($data, $options = array()) {
 
  $curly = array();
  $result = array();
  $mh = curl_multi_init();
 
  foreach ($data as $id => $d) {
 
        $curly[$id] = curl_init();

        $url = (is_array($d) && !empty($d['url'])) ? $d['url'] : $d;
        curl_setopt($curly[$id], CURLOPT_URL,            $url);
        curl_setopt($curly[$id], CURLOPT_HEADER,         0);
        curl_setopt($curly[$id], CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($curly[$id], CURLOPT_SSL_VERIFYPEER, false);
        // post?
        if (is_array($d)) {
          if (!empty($d['post'])) {
            curl_setopt($curly[$id], CURLOPT_POST,       1);
            curl_setopt($curly[$id], CURLOPT_POSTFIELDS, $d['post']);
          }
        }

        // extra options?
        if (!empty($options)) {
          curl_setopt_array($curly[$id], $options);
        }
        curl_multi_add_handle($mh, $curly[$id]);
  }
 
  $running = null;
  do {
    curl_multi_exec($mh, $running);
  } while($running > 0);
 
 
  foreach($curly as $id => $c) {
    $result[$id] = curl_multi_getcontent($c);
    curl_multi_remove_handle($mh, $c);
  }

  curl_multi_close($mh);
 
  return $result;
}

function GET_HTML_FOR_URL($url){
    
     $ch = curl_init();  
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1); 
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204 Safari/534.16");
    curl_setopt($ch, CURLOPT_URL, $url); 
    return curl_exec($ch);
}


if($_GET["vendor"] == "cell_signalling"){
    
    
    $url = "https://www.cellsignal.com/browse/western-blot/primary-antibodies?Ntk=Products&N=4294956287&Ntt=";
	$url .= $_GET["search_text"];
    $url .= '&site-search-type=Products';
    $result_html = GET_HTML_FOR_URL($url);
    
    
    $doc = new DOMDocument();
    $doc->loadHTML($result_html);
    $XPath = new DOMXPath($doc);    
    $links = $XPath->query('.//*[@id="product-list"]//tr/td[1]//a[contains(@href, "primary-antibodies") and not(contains(@href, "sampler"))]');
    
    
    $info_objects = array();
    $urls = array();
 
    foreach($links as $link){
        
        $href = $link->getAttribute("href");
        
        $info_object = array();
        $info_object["url"] = "https://www.cellsignal.com".$href;
        $info_object["vendor"] = "Cell Signalling";
        array_push($info_objects, $info_object);
        array_push($urls, $info_object["url"]);
    }   
    
    
    $responses = MULTI_REQUEST($urls);
    foreach($responses as $index => $response){
        
        $doc = new DOMDocument();
        $doc->loadHTML($response);
        $XPath = new DOMXPath($doc);    
       
        $titles = $XPath->query('.//h1[@class="title"]');
        $mw_nodes = $XPath->query('.//*[@id="standard-table"]//tr[(count(preceding-sibling::*)+1) = 2]//td[(count(preceding-sibling::*)+1) = 3]');
        
        $species = $XPath->query('//*[@id="standard-table"]//tr[2]/td[4]');
        if($species->length > 0)  $info_objects[$index]["species"] =  preg_replace("/igg\w{0,}/", "", strtolower(trim($species->item(0)->nodeValue)));
        
        if($titles->length > 0) $info_objects[$index]["title"] = $titles->item(0)->nodeValue;
        else $info_objects[$index]["title"] = "null";
         
       
        if($mw_nodes->length > 0) {
            $info_objects[$index]["mw"] = trim($mw_nodes->item(0)->nodeValue);
            
            $mw = trim($mw_nodes->item(0)->nodeValue);
            preg_match_all('/\d+/', $mw, $matches);
            $match = $matches[0];
            if(count($match) > 0){
                
                 $info_objects[$index]["mw"] = array_sum($match)/count($match);
            }
            else $info_objects[$index]["mw"] = "null";
        }
        
        else $info_objects[$index]["mw"] = "null";
    }
    
    
    if(count($info_objects) > 0){
        
         RETURN_RESPONSE(1, "products_were_found", $info_objects);
    }
    else{
        
        RETURN_RESPONSE(0, "products_were_not_found", $info_objects);
    }
    
}

if($_GET["vendor"] == "abcam"){
    
   $url = "https://www.abcam.com/products?sortOptions=Relevance&keywords=".$_GET["search_text"]."&selected.classification=Primary+antibodies&selected.application=WB";
    $result_html = GET_HTML_FOR_URL($url);
    
    
    $doc = new DOMDocument();
    $doc->loadHTML($result_html);
    $XPath = new DOMXPath($doc);    
    $links = $XPath->query('//*[@id="search_result_container"]//div[@class="pws-item-info"]//h3//a');
    
    
    $info_objects = array();
    $urls = array();
 
    foreach($links as $link){
        
        $href = $link->getAttribute("href");
        
        $info_object = array();
        $info_object["url"] = "https://www.abcam.com".$href;
        $info_object["vendor"] = "Abcam";
        array_push($info_objects, $info_object);
        array_push($urls, $info_object["url"]);
    }       
    
    $responses = MULTI_REQUEST($urls);
    foreach($responses as $index => $response){
        
        $doc = new DOMDocument();
        $doc->loadHTML($response);
        $XPath = new DOMXPath($doc);    
        
        
        $titles = $XPath->query('.//h1[@class="title"]');
        if($titles->length > 0) $info_objects[$index]["title"] = $titles->item(0)->nodeValue;
        else $info_objects[$index]["title"] = "null";
        
        
        $species = $XPath->query('//*[@id="description_primaries_suboverview"]//ul//li[3]//div[2]');
        if($species->length > 0)  $info_objects[$index]["species"] =  strtolower(trim($species->item(0)->nodeValue));
        
        
        
       
        $mw_nodes = $XPath->query('//*[@id="description_applications"]//table//tr[td//abbr//text()[contains(.,"WB")]]//td[last()]');
                
        if($mw_nodes->length > 0){
         
            
            $mw_text = trim($mw_nodes->item(0)->nodeValue);
            preg_match_all('/\d+\s{0,}kD/', $mw_text, $matches);

            $match = $matches[0];
            if(count($match) > 0){
                
                 $info_objects[$index]["mw"] = str_replace("kD", "", $match[0]);
            }
            else $info_objects[$index]["mw"] = "null";
        }
        else $info_objects[$index]["mw"] = "null";
    }
    
    
    if(count($info_objects) > 0)RETURN_RESPONSE(1, "products_were_found", $info_objects);
    else RETURN_RESPONSE(0, "products_were_not_found", $info_objects);
}

if($_GET["vendor"] == "santa_cruz_biotech"){
    
     $url = "https://www.scbt.com/scbt/search/_/N-1fskn35?refinement=true&Nr=AND%28product.siteId%3AscbtSite%2COR%28product.catalogId%3AscbtCatalog%29%2Cproduct.webDisplayFlag%3A1%2Cproduct.suppressDisplayFlag%3A0%29&Ntt=".$_GET["search_text"];
    $result_html = GET_HTML_FOR_URL($url);
    
    
    $doc = new DOMDocument();
    $doc->loadHTML($result_html);
    $XPath = new DOMXPath($doc);    
    $links = $XPath->query('//table//td[@data-label="PRODUCT NAME"]//a');
    $pdf_links = $XPath->query('//table//td[@data-label="Catalog #"]//a');
    
    $info_objects = array();
    $urls = array();
 
    foreach($links as $index =>$link){
        
        $href = $link->getAttribute("href");
        
        $info_object = array();
        $info_object["url"] = $href;
         $info_object["title"] = $link->nodeValue;
        $info_object["vendor"] = "Santa Cruz Bio";
        array_push($info_objects, $info_object);
        
        $pdf_url = "https://datasheets.scbt.com/".$pdf_links->item($index)->nodeValue.".pdf";
        array_push($urls, $pdf_url);
    }  
    
    
    $responses = MULTI_REQUEST($urls);
    
    
    foreach($responses as $index => $response){
        
        $text = PdfParser::parseContent($response);
        preg_match_all('/\d+\s{0,}kDa/', $text, $matches);
        $match = $matches[0];
        if(count($match) > 0){

             $info_objects[$index]["mw"] = str_replace("kDa", "", $match[0]);
        }
        else $info_objects[$index]["mw"] = "null";
        
         preg_match_all('/is a\s{0,}\w{0,}\s{0,}monoclonal\s{0,}antibody/', $text, $matches);
        $match = $matches[0];
        if(count($match) > 0){
            
            
            $species = str_replace("monoclonal antibody", "", $match[0]);
             $species = str_replace("is a", "", $species);
            
            $info_objects[$index]["species"] = $species;
        }
        
        /*
        if(strpos($text, "is a mouse monoclonal antibody") !== false){
            
            $info_objects[$index]["species"] =  "Mouse";
        }
        else  if(strpos($text, "is a rabbit monoclonal antibody") !== false){
            
            $info_objects[$index]["species"] =  "Rabbit";
        }
        */
        
        
    }
    
    if(count($info_objects) > 0)RETURN_RESPONSE(1, "products_were_found", $info_objects);
    else RETURN_RESPONSE(0, "products_were_not_found", $info_objects);
}




function GET_BASE_PRODUCT_LIST_FROM_VENDOR($vendor, $url, $xpath, $query){
    
    $result_html = GET_HTML_FOR_URL($url);
    
    $base_url = substr($url, 0, strpos($url, ".com") + 4);
    
    $doc = new DOMDocument();
    $doc->loadHTML($result_html);
    $XPath = new DOMXPath($doc);    
   
    $links = $XPath->query($xpath);
    
    
    
    
    $info_objects = array();
    $urls = array();
 
    foreach($links as $link){
        
        $href = $link->getAttribute("href");
        
        $info_object = array();
        $info_object["url"] = $base_url.$href;
        $info_object["vendor"] = $vendor;
        array_push($info_objects, $info_object);
    }   
    
    return $info_objects;
}

function GET_MW_FROM_URLs($urls, $xpath){
    
    $responses = MULTI_REQUEST($urls);
    foreach($responses as $index => $response){
        
        $doc = new DOMDocument();
        $doc->loadHTML($response);
        $XPath = new DOMXPath($doc);    
       
        $mw_nodes = $XPath->query($xpath);

       
        if($mw_nodes->length > 0) {
            $info_objects[$index]["mw"] = trim($mw_nodes->item(0)->nodeValue);
            
            $mw = trim($mw_nodes->item(0)->nodeValue);
            preg_match_all('/\d+/', $mw, $matches);
            $match = $matches[0];
            if(count($match) > 0){
                
                 $info_objects[$index]["mw"] = array_sum($match)/count($match);
            }
            else $info_objects[$index]["mw"] = "null";
        }
        
        else $info_objects[$index]["mw"] = "null";
    }
    
    
}

?>
