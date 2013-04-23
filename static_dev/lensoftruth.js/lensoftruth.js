/*
 * James D. Zoll
 *
 * 4/22/2013
 *
 * Lens of Truth jQuery plugin.
 *
 * This is a simple plugin that overrides the jQuery .data() function
 * to actually write values out to the DOM when setting them. jQuery by
 * default stores the values in an internal cache for speed and compatibility
 * reasons, but this makes it tedious to debug data-attribute related 
 * behavior, particularly on browsers without mature developer tools, since
 * it can be difficult to grab expando properties on nodes.
 *
 * This plugin is very minimal, but should still only be run when debugging.
 * Data properties will have the string "data-lot" prepended to their name
 * to prevent jQuery from re-fetching them from the DOM, and to remove 
 * possible DEBUG only behavior. 
 *
 * Non-string literals passed in will be converted to JSON values before
 * being added to the DOM, if the browser supports it. In the interest of
 * being lightweight, browsers that don't have native JSON object will just
 * print the [object Object] or similar, since jQuery doesn't have a built
 * in toJson().
 */

(function( $ ){
  
  // Prefix for all attributes written to the DOM
  var attrPrefix = 'data-lot-';

  // Store a handle for the old data function.
  var _oldData = $.fn.data;
  
  // We define a function to write out attributes. It will be aware
  // of both the attrPrefix value and of the reserved names for
  // data objects that jQuery uses, which will not be written
  // to the dom.
  var writeAttr = function(obj, k, v) {
    if (!(k[0] === '_' || k === 'events' || k === 'handle')) {
      if (typeof v === 'object' && window.JSON && window.JSON.stringify) {
        obj.attr(attrPrefix + k, window.JSON.stringify(v));
        return;
      }
      obj.attr(attrPrefix + k, v);
    }
  };
  
  $.fn.data = function(key, value) {
    
    // Call the jQuery data function and store the result.
    // Do this first so that if it raises an exception, we 
    // don't modify the DOM.
    var result = _oldData.apply(this, arguments);
    
    // Now depending on whether we have a key, a key and a value,
    // or an object, update the DOM appropriately.
    if (key === undefined) {
      // Nothing to write, since this was a fetch.
      return result;
    }
    if (typeof key === 'object') {
      // Multiple values were set, so iterate and
      // write them all.
      var elems = this;
      $.each(key, function(k, v) {
        writeAttr(elems, k, v);
      });
      return result;
    }
    if (value === undefined) {
      // Nothing to write, since this was a fetch.
      return result;
    }
    // Write the single attribute to the DOM.
    writeAttr(this, key, value);
    return result;
  };
})( jQuery );