module CarouselHelper
  def carousel(id, options={}, init_on_load = true, &block)        
    ul  = content_tag "ul", (block_given? ? yield : ""), :class => "carousel-list"
    clip  = content_tag "div", ul, :class => "carousel-clip-region"
    content_tag "div", clip, :id => id, :class => "carousel-component"
    
    jid = id.gsub(/-/, "_")
    js = "function initCarousel_#{jid}() {var carousel = new Carousel('#{id}', #{options_for_javascript(options)})};"
    js += init_on_load ? "Event.observe(window, 'load', initCarousel_#{jid});" : "initCarousel_#{jid}()"
    
    content_tag("div", clip, :id => id, :class => "carousel-component") + javascript_tag(js)
  end

  private
  ## Extend options_for_javascript to handle hashmap of hashmap
  def options_for_javascript(options)
    '{' + options.map {|k, v|  v.kind_of?(Hash) ? "#{k}:#{options_for_javascript(v)}" : "#{k}:#{v}"}.sort.join(', ') + '}'
  end  
end
